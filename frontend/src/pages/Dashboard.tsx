import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Typography,
  Table,
  Tag,
  Progress,
  Space,
  Button,
  DatePicker,
  Select
} from 'antd';
import {
  ProjectOutlined,
  BugOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { useAuth } from '../hooks/useAuth';
import { projectAPI, executionAPI } from '../services/api';
import type { Project, TestExecution } from '../types';

const { Title } = Typography;
const { RangePicker } = DatePicker;

const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [recentExecutions, setRecentExecutions] = useState<TestExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(7, 'day'),
    dayjs()
  ]);
  
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projectsData] = await Promise.all([
        projectAPI.getProjects({ limit: 10 })
      ]);
      
      setProjects(projectsData);
      
      // 获取每个项目的最近执行记录
      const executionsPromises = projectsData.map(project =>
        executionAPI.getExecutions(project.id, { limit: 5 })
          .catch(() => []) // 忽略错误，返回空数组
      );
      
      const executionsResults = await Promise.all(executionsPromises);
      const allExecutions = executionsResults.flat();
      
      // 按时间排序，获取最近10条
      const sortedExecutions = allExecutions
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, 10);
      
      setRecentExecutions(sortedExecutions);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // 计算统计数据
  const stats = {
    totalProjects: projects.length,
    totalExecutions: recentExecutions.length,
    passedExecutions: recentExecutions.filter(e => e.status === 'passed').length,
    failedExecutions: recentExecutions.filter(e => e.status === 'failed').length,
    runningExecutions: recentExecutions.filter(e => e.status === 'running').length,
  };

  const passRate = stats.totalExecutions > 0 
    ? Math.round((stats.passedExecutions / stats.totalExecutions) * 100)
    : 0;

  const executionColumns = [
    {
      title: '执行ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '项目',
      dataIndex: 'projectId',
      key: 'projectId',
      render: (projectId: number) => {
        const project = projects.find(p => p.id === projectId);
        return project?.name || `项目 ${projectId}`;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          pending: { color: 'default', icon: <ClockCircleOutlined /> },
          running: { color: 'processing', icon: <PlayCircleOutlined /> },
          passed: { color: 'success', icon: <CheckCircleOutlined /> },
          failed: { color: 'error', icon: <CloseCircleOutlined /> },
        };
        
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config.color} icon={config.icon}>
            {status.toUpperCase()}
          </Tag>
        );
      },
    },
    {
      title: '开始时间',
      dataIndex: 'startTime',
      key: 'startTime',
      render: (time: string) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '耗时',
      key: 'duration',
      render: (record: TestExecution) => {
        if (!record.startTime || !record.endTime) return '-';
        const duration = dayjs(record.endTime).diff(dayjs(record.startTime), 'second');
        return `${duration}s`;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (record: TestExecution) => (
        <Space size="small">
          <Button 
            size="small" 
            onClick={() => navigate(`/executions/${record.id}`)}
          >
            查看详情
          </Button>
          {record.reportPath && (
            <Button 
              size="small" 
              type="link"
              onClick={() => window.open(`/reports/${record.reportPath}`, '_blank')}
            >
              查看报告
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>仪表板</Title>
        <p>欢迎回来，{user?.username}！这里是您的测试平台概览。</p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={stats.totalProjects}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="执行总数"
              value={stats.totalExecutions}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="通过率"
              value={passRate}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: passRate >= 80 ? '#52c41a' : '#ff4d4f' }}
            />
            <Progress 
              percent={passRate} 
              showInfo={false} 
              strokeColor={passRate >= 80 ? '#52c41a' : '#ff4d4f'}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.runningExecutions}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近执行记录 */}
      <Card
        title="最近执行记录"
        extra={
          <Space>
            <Button onClick={() => navigate('/executions')}>
              查看全部
            </Button>
          </Space>
        }
      >
        <Table
          columns={executionColumns}
          dataSource={recentExecutions}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 800 }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;

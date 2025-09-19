import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Card,
  Space,
  Typography,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Tag
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ProjectOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { projectAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import type { Project } from '../types';

const { Title } = Typography;
const { TextArea } = Input;

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();
  
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await projectAPI.getProjects();
      setProjects(data);
    } catch (error) {
      message.error('获取项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProject(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    form.setFieldsValue(project);
    setModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingProject) {
        // 更新项目
        await projectAPI.updateProject(editingProject.id, values);
        message.success('项目更新成功');
      } else {
        // 创建项目
        await projectAPI.createProject(values);
        message.success('项目创建成功');
      }
      
      setModalVisible(false);
      fetchProjects();
    } catch (error) {
      console.error('Submit failed:', error);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await projectAPI.deleteProject(id);
      message.success('项目删除成功');
      fetchProjects();
    } catch (error) {
      message.error('删除项目失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Project) => (
        <Button 
          type="link" 
          onClick={() => navigate(`/projects/${record.id}`)}
          style={{ padding: 0 }}
        >
          {text}
        </Button>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '仓库地址',
      dataIndex: 'repositoryUrl',
      key: 'repositoryUrl',
      render: (url: string) => url ? (
        <a href={url} target="_blank" rel="noopener noreferrer">
          {url}
        </a>
      ) : '-',
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '状态',
      key: 'status',
      render: () => <Tag color="green">活跃</Tag>,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: Project) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={user?.role !== 'admin' && record.createdBy !== user?.id}
          >
            编辑
          </Button>
          <Button
            size="small"
            onClick={() => navigate(`/projects/${record.id}/test-cases`)}
          >
            测试用例
          </Button>
          <Button
            size="small"
            onClick={() => navigate(`/projects/${record.id}/executions`)}
          >
            执行历史
          </Button>
          {(user?.role === 'admin' || record.createdBy === user?.id) && (
            <Popconfirm
              title="确定要删除这个项目吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: 16 
        }}>
          <Title level={3} style={{ margin: 0 }}>
            <ProjectOutlined /> 项目管理
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建项目
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={loading}
          pagination={{
            total: projects.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个项目`,
          }}
        />
      </Card>

      <Modal
        title={editingProject ? '编辑项目' : '新建项目'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          name="projectForm"
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[
              { required: true, message: '请输入项目名称' },
              { max: 100, message: '项目名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="输入项目名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="项目描述"
            rules={[
              { max: 500, message: '项目描述不能超过500个字符' }
            ]}
          >
            <TextArea 
              rows={4} 
              placeholder="输入项目描述（可选）" 
            />
          </Form.Item>

          <Form.Item
            name="repositoryUrl"
            label="仓库地址"
            rules={[
              { type: 'url', message: '请输入有效的URL地址' }
            ]}
          >
            <Input placeholder="输入Git仓库地址（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Projects;

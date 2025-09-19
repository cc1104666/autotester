import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Tabs, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { LoginForm, RegisterForm } from '../types';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user, login, register } = useAuth();

  // 如果已登录，重定向到首页
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogin = async (values: LoginForm) => {
    setLoading(true);
    const success = await login(values);
    if (success) {
      navigate('/dashboard');
    }
    setLoading(false);
  };

  const handleRegister = async (values: RegisterForm) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    const success = await register(values);
    if (success) {
      setActiveTab('login');
    }
    setLoading(false);
  };

  const loginForm = (
    <Form
      name="login"
      size="large"
      onFinish={handleLogin}
      autoComplete="off"
    >
      <Form.Item
        name="username"
        rules={[{ required: true, message: '请输入用户名' }]}
      >
        <Input 
          prefix={<UserOutlined />} 
          placeholder="用户名" 
        />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: '请输入密码' }]}
      >
        <Input.Password 
          prefix={<LockOutlined />} 
          placeholder="密码" 
        />
      </Form.Item>

      <Form.Item>
        <Button 
          type="primary" 
          htmlType="submit" 
          block 
          loading={loading}
        >
          登录
        </Button>
      </Form.Item>
    </Form>
  );

  const registerForm = (
    <Form
      name="register"
      size="large"
      onFinish={handleRegister}
      autoComplete="off"
    >
      <Form.Item
        name="username"
        rules={[
          { required: true, message: '请输入用户名' },
          { min: 3, message: '用户名至少3个字符' }
        ]}
      >
        <Input 
          prefix={<UserOutlined />} 
          placeholder="用户名" 
        />
      </Form.Item>

      <Form.Item
        name="email"
        rules={[
          { required: true, message: '请输入邮箱' },
          { type: 'email', message: '请输入有效的邮箱地址' }
        ]}
      >
        <Input 
          prefix={<MailOutlined />} 
          placeholder="邮箱" 
        />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[
          { required: true, message: '请输入密码' },
          { min: 6, message: '密码至少6个字符' }
        ]}
      >
        <Input.Password 
          prefix={<LockOutlined />} 
          placeholder="密码" 
        />
      </Form.Item>

      <Form.Item
        name="confirmPassword"
        rules={[
          { required: true, message: '请确认密码' }
        ]}
      >
        <Input.Password 
          prefix={<LockOutlined />} 
          placeholder="确认密码" 
        />
      </Form.Item>

      <Form.Item>
        <Button 
          type="primary" 
          htmlType="submit" 
          block 
          loading={loading}
        >
          注册
        </Button>
      </Form.Item>
    </Form>
  );

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card 
        style={{ width: 400, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}
        bordered={false}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ color: '#1890ff', marginBottom: 8 }}>
            自动化测试平台
          </Title>
          <Text type="secondary">
            智能化测试管理解决方案
          </Text>
        </div>

        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          centered
          items={[
            {
              key: 'login',
              label: '登录',
              children: loginForm
            },
            {
              key: 'register',
              label: '注册',
              children: registerForm
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default Login;

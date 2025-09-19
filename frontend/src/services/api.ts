import axios, { AxiosResponse } from 'axios';
import { message } from 'antd';
import type { 
  User, 
  Project, 
  TestCase, 
  TestExecution,
  Environment,
  LoginForm, 
  RegisterForm, 
  AuthToken,
  ApiResponse 
} from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      message.error('服务器错误，请稍后重试');
    } else if (error.response?.data?.detail) {
      message.error(error.response.data.detail);
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authAPI = {
  // 登录
  login: async (data: LoginForm): Promise<AuthToken> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post<AuthToken>('/auth/login', formData);
    return response.data;
  },

  // 注册
  register: async (data: RegisterForm): Promise<User> => {
    const response = await api.post<User>('/auth/register', {
      username: data.username,
      email: data.email,
      password: data.password,
    });
    return response.data;
  },

  // 获取当前用户信息
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// 项目相关API
export const projectAPI = {
  // 获取项目列表
  getProjects: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get<Project[]>('/projects', { params });
    return response.data;
  },

  // 获取项目详情
  getProject: async (id: number): Promise<Project> => {
    const response = await api.get<Project>(`/projects/${id}`);
    return response.data;
  },

  // 创建项目
  createProject: async (data: Omit<Project, 'id' | 'createdBy' | 'createdAt' | 'updatedAt'>): Promise<Project> => {
    const response = await api.post<Project>('/projects', data);
    return response.data;
  },

  // 更新项目
  updateProject: async (id: number, data: Partial<Project>): Promise<Project> => {
    const response = await api.put<Project>(`/projects/${id}`, data);
    return response.data;
  },

  // 删除项目
  deleteProject: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

// 测试用例相关API
export const testCaseAPI = {
  // 获取测试用例列表
  getTestCases: async (projectId: number, params?: { 
    skip?: number; 
    limit?: number; 
    testType?: string; 
  }) => {
    const response = await api.get<TestCase[]>(`/projects/${projectId}/test-cases`, { params });
    return response.data;
  },

  // 获取测试用例详情
  getTestCase: async (id: number): Promise<TestCase> => {
    const response = await api.get<TestCase>(`/test-cases/${id}`);
    return response.data;
  },

  // 创建测试用例
  createTestCase: async (projectId: number, data: Omit<TestCase, 'id' | 'projectId' | 'createdBy' | 'createdAt' | 'updatedAt'>): Promise<TestCase> => {
    const response = await api.post<TestCase>(`/projects/${projectId}/test-cases`, data);
    return response.data;
  },

  // 更新测试用例
  updateTestCase: async (id: number, data: Partial<TestCase>): Promise<TestCase> => {
    const response = await api.put<TestCase>(`/test-cases/${id}`, data);
    return response.data;
  },

  // 删除测试用例
  deleteTestCase: async (id: number): Promise<void> => {
    await api.delete(`/test-cases/${id}`);
  },
};

// 测试执行相关API
export const executionAPI = {
  // 获取执行历史
  getExecutions: async (projectId: number, params?: { skip?: number; limit?: number }) => {
    const response = await api.get<TestExecution[]>(`/projects/${projectId}/executions`, { params });
    return response.data;
  },

  // 获取执行详情
  getExecution: async (id: number): Promise<TestExecution> => {
    const response = await api.get<TestExecution>(`/executions/${id}`);
    return response.data;
  },

  // 执行测试
  executeTests: async (projectId: number, data: {
    environmentId: number;
    testCaseIds?: number[];
  }): Promise<TestExecution> => {
    const response = await api.post<TestExecution>(`/projects/${projectId}/execute`, data);
    return response.data;
  },

  // 停止执行
  stopExecution: async (id: number): Promise<void> => {
    await api.post(`/executions/${id}/stop`);
  },
};

export default api;

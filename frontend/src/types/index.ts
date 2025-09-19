// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'tester' | 'viewer';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// 项目类型
export interface Project {
  id: number;
  name: string;
  description?: string;
  repositoryUrl?: string;
  createdBy: number;
  createdAt: string;
  updatedAt: string;
}

// 环境类型
export interface Environment {
  id: number;
  projectId: number;
  name: string;
  baseUrl?: string;
  config?: Record<string, any>;
  createdAt: string;
}

// 测试用例类型
export interface TestCase {
  id: number;
  projectId: number;
  name: string;
  type: 'api' | 'ui';
  description?: string;
  testData?: Record<string, any>;
  createdBy: number;
  createdAt: string;
  updatedAt: string;
}

// 测试执行类型
export interface TestExecution {
  id: number;
  projectId: number;
  environmentId: number;
  status: 'pending' | 'running' | 'passed' | 'failed';
  startTime?: string;
  endTime?: string;
  result?: Record<string, any>;
  reportPath?: string;
  createdBy: number;
  createdAt: string;
}

// API响应类型
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// 分页类型
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

// 登录表单类型
export interface LoginForm {
  username: string;
  password: string;
}

// 注册表单类型
export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

// Token类型
export interface AuthToken {
  access_token: string;
  token_type: string;
}

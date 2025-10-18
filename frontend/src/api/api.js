import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * 获取指定作业的排行榜
 * @param {string} assignmentId - 作业ID
 * @returns {Promise<Array>} 排行榜数据
 */
export const getLeaderboard = (assignmentId) => {
  return api.get(`/leaderboard/${assignmentId}`);
};

/**
 * 获取所有排行榜
 * @returns {Promise<Object>} 所有排行榜数据（按作业ID分组）
 */
export const getAllLeaderboards = () => {
  return api.get('/leaderboard');
};

/**
 * 获取学生的所有提交记录
 * @param {string} studentId - 学生ID
 * @param {string} assignmentId - 作业ID
 * @returns {Promise<Array>} 提交记录列表
 */
export const getStudentSubmissions = (studentId, assignmentId) => {
  return api.get(`/submissions/${studentId}/${assignmentId}`);
};

/**
 * 提交作业
 * @param {Object} submissionData - 提交数据
 * @returns {Promise<Object>} 提交结果
 */
export const submitAssignment = (submissionData) => {
  return api.post('/submit', submissionData);
};

/**
 * 健康检查
 * @returns {Promise<Object>} 健康状态
 */
export const healthCheck = () => {
  return api.get('/health');
};

/**
 * 获取所有作业配置
 * @returns {Promise<Object>} 所有作业配置
 */
export const getAllAssignments = () => {
  return api.get('/assignments');
};

export default api;


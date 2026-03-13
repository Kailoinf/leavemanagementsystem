import { BASE_URL } from '@/app';

// 统一的 API 请求函数
export const request = (options: {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: any;
}) => {
  const token = wx.getStorageSync('token');
  
  // 默认配置
  const defaultOptions = {
    url: `${BASE_URL}${options.url}`,
    method: options.method || 'GET',
    data: {
      ...options.data,
      token // 自动添加 token
    },
    header: {
      'content-type': 'application/json',
      ...options.header
    }
  };

  return new Promise((resolve, reject) => {
    wx.request({
      ...defaultOptions,
      success: (res) => {
        resolve(res);
      },
      fail: (error) => {
        console.error('请求失败:', error);
        reject(error);
      }
    });
  });
};
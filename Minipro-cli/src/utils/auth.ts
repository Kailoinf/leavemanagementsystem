import { BASE_URL } from '@/app';

export interface UserInfo {
  role: string;
  id: string;
  name: string;
}

// 检查登录状态
export const checkLoginStatus = (): Promise<{ success: boolean; userInfo?: UserInfo }> => {
  return new Promise((resolve) => {
    const token = wx.getStorageSync('token');
    const localUserInfo = wx.getStorageSync('userInfo');

    // 如果没有token，返回失败
    if (!token) {
      resolve({ success: false });
      return;
    }

    // 如果有本地用户信息，先返回本地信息，然后在后台验证
    if (localUserInfo) {
      resolve({ success: true, userInfo: localUserInfo });
      
      // 后台验证token有效性
      wx.request({
        url: `${BASE_URL}/login/check`,
        method: 'GET',
        data: { token },
        success: (res) => {
          if (res.statusCode === 200 && res.data && typeof res.data === 'object' && !Array.isArray(res.data)) {
            // 更新本地用户信息
            const userInfo: UserInfo = {
              role: (res.data as Record<string, any>).role,
              id: (res.data as Record<string, any>).id,
              name: (res.data as Record<string, any>).name
            };
            wx.setStorageSync('userInfo', userInfo);
          } else {
            // token失效，清除本地存储
            console.warn('Token验证失败，清除本地存储');
            wx.removeStorageSync('token');
            wx.removeStorageSync('userInfo');
          }
        },
        fail: (err) => {
          console.warn('Token验证请求失败，网络问题但不影响当前登录状态:', err);
          // 网络失败时不清除本地存储，保持登录状态
        }
      });
    } else {
      // 没有本地用户信息，需要验证token
      wx.request({
        url: `${BASE_URL}/login/check`,
        method: 'GET',
        data: { token },
        success: (res) => {
          if (res.statusCode === 200 && res.data && typeof res.data === 'object' && !Array.isArray(res.data)) {
            const userInfo: UserInfo = {
              role: (res.data as Record<string, any>).role,
              id: (res.data as Record<string, any>).id,
              name: (res.data as Record<string, any>).name
            };

            wx.setStorageSync('userInfo', userInfo);
            resolve({ success: true, userInfo });
          } else {
            wx.removeStorageSync('token');
            wx.removeStorageSync('userInfo');
            resolve({ success: false });
          }
        },
        fail: () => {
          resolve({ success: false });
        }
      });
    }
  });
};

// 获取本地用户信息
export const getLocalUserInfo = (): UserInfo | null => {
  return wx.getStorageSync('userInfo') || null;
};

// 检查是否需要登录
export const requireAuth = async () => {
  const { success, userInfo } = await checkLoginStatus();

  if (!success) {
    // 跳转到登录页
    wx.redirectTo({
      url: '/pages/login/index'
    });
    return false;
  }

  return userInfo;
};

// 退出登录
export const logout = async () => {
  const token = wx.getStorageSync('token');

  if (token) {
    // 调用退出登录API
    wx.request({
      url: `${BASE_URL}/logout`,
      method: 'GET',
      data: { token },
      success: () => {
        // 清除本地存储
        wx.removeStorageSync('token');
        wx.removeStorageSync('userInfo');
        wx.redirectTo({
          url: '/pages/login/index'
        });
      },
      fail: () => {
        // 即使API调用失败，也清除本地存储
        wx.removeStorageSync('token');
        wx.removeStorageSync('userInfo');
        wx.redirectTo({
          url: '/pages/login/index'
        });
      }
    });
  } else {
    // 没有token直接跳转登录页
    wx.redirectTo({
      url: '/pages/login/index'
    });
  }
};
import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app';

interface LoginFormData {
  id: string;
  password: string;
}

interface UserInfo {
  role: string;
  id: string;
  name: string;
}

export default defineComponent(() => {
  const loginForm = ref<LoginFormData>({
    id: '',
    password: ''
  });

  const loading = ref(false);
  const rememberPassword = ref(false);

  // 检查是否已经登录
  const checkAlreadyLoggedIn = () => {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      // 已经登录，直接跳转到主页
      wx.switchTab({
        url: '/pages/home/index'
      });
      return true;
    }
    return false;
  };

  // 加载保存的登录信息
  const loadSavedCredentials = () => {
    const savedId = wx.getStorageSync('savedUserId');
    const savedPassword = wx.getStorageSync('savedPassword');
    const savedRemember = wx.getStorageSync('rememberPassword');
    
    if (savedId) {
      loginForm.value.id = savedId;
    }
    if (savedPassword && savedRemember) {
      loginForm.value.password = savedPassword;
      rememberPassword.value = true;
    }
  };

  // 保存登录信息
  const saveCredentials = () => {
    if (rememberPassword.value) {
      wx.setStorageSync('savedUserId', loginForm.value.id);
      wx.setStorageSync('savedPassword', loginForm.value.password);
      wx.setStorageSync('rememberPassword', true);
    } else {
      wx.removeStorageSync('savedUserId');
      wx.removeStorageSync('savedPassword');
      wx.removeStorageSync('rememberPassword');
    }
  };

  // 页面加载时检查登录状态
  const onLoad = () => {
    if (checkAlreadyLoggedIn()) {
      return;
    }
    loadSavedCredentials();
  };

  // 生成稳定token，基于用户ID和时间戳
  const generateToken = (userId: string) => {
    const timestamp = Date.now().toString();
    const userHash = btoa(userId).replace(/[^a-zA-Z0-9]/g, '').substring(0, 8);
    return `${userHash}_${timestamp}`;
  };

  // 登录请求
  const handleLogin = async () => {
    if (!loginForm.value.id || !loginForm.value.password) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    loading.value = true;
    saveCredentials(); // 保存登录信息

    try {
      const token = generateToken(loginForm.value.id);

      const requestData = {
        id: parseInt(loginForm.value.id) || loginForm.value.id,
        password: loginForm.value.password,
        token: token
      };

      console.log('发送登录请求:', `${BASE_URL}/login`);
      console.log('请求数据:', requestData);
      console.log('BASE_URL:', BASE_URL);

      wx.request({
        url: `${BASE_URL}/login`,
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        data: requestData,
        success: (res) => {
          console.log('登录响应:', res);
          if (res.statusCode === 200 && res.data && typeof res.data === 'object') {
            // 登录成功，从后端返回值中获取角色信息
            const response = res.data as any;
            const userInfo: UserInfo = {
              role: response.role || '',
              id: response.id || loginForm.value.id,
              name: response.name || ''
            };

            wx.setStorageSync('token', token);
            wx.setStorageSync('userInfo', userInfo);

            wx.showToast({
              title: '登录成功',
              icon: 'success'
            });

            // 延迟跳转到主页
            setTimeout(() => {
              wx.switchTab({
                url: '/pages/home/index'
              });
            }, 1500);
          } else {
            console.error('登录响应异常:', res);
            wx.showToast({
              title: `登录失败: ${res.statusCode || '未知错误'}`,
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          console.error('登录请求失败:', err);
          wx.showToast({
            title: '网络错误，请重试',
            icon: 'none'
          });
        },
        complete: () => {
          loading.value = false;
        }
      });
    } catch (error) {
      console.error('登录异常:', error);
      loading.value = false;
      wx.showToast({
        title: '登录异常，请重试',
        icon: 'none'
      });
    }
  };

  // 处理账号输入
  const onIdInput = (e: any) => {
    loginForm.value.id = e.detail.value;
  };

  // 处理密码输入
  const onPasswordInput = (e: any) => {
    loginForm.value.password = e.detail.value;
  };

  // 处理记住密码切换
  const onRememberPasswordChange = (e: any) => {
    rememberPassword.value = e.detail.value;
  };

  return {
    loginForm,
    loading,
    rememberPassword,
    handleLogin,
    onIdInput,
    onPasswordInput,
    onRememberPasswordChange,
    onLoad
  };
});
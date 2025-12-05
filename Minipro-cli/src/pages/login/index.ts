import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app';

interface LoginFormData {
  role: string;
  id: string;
  password: string;
}

interface UserInfo {
  role: string;
  id: string;
  name: string;
}

defineComponent(() => {
  const loginForm = ref<LoginFormData>({
    role: 'student',
    id: '',
    password: ''
  });

  const loading = ref(false);
  const roleOptions = [
    { value: 'student', text: '学生' },
    { value: 'teacher', text: '教师' },
    { value: 'admin', text: '管理员' }
  ];

  const selectedRoleIndex = ref(0); // 默认选中第一个角色

  // 生成唯一token
  const generateToken = () => {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
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

    try {
      const token = generateToken();

      const requestData = {
        role: loginForm.value.role,
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
            // 登录成功，保存token和用户信息
            const response = res.data as any;
            const userInfo: UserInfo = {
              role: response.role || '',
              id: response.id || '',
              name: response.name || ''
            };

            wx.setStorageSync('token', token);
            wx.setStorageSync('userInfo', userInfo);

            wx.showToast({
              title: '登录成功',
              icon: 'success'
            });

            // 延迟跳转到mine页面
            setTimeout(() => {
              wx.switchTab({
                url: '/pages/mine/index'
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

  // 处理角色选择
  const onRoleChange = (e: any) => {
    const index = e.detail.value;
    selectedRoleIndex.value = index;
    loginForm.value.role = roleOptions[index].value;
  };

  // 处理账号输入
  const onIdInput = (e: any) => {
    loginForm.value.id = e.detail.value;
  };

  // 处理密码输入
  const onPasswordInput = (e: any) => {
    loginForm.value.password = e.detail.value;
  };

  return {
    loginForm,
    loading,
    roleOptions,
    selectedRoleIndex,
    handleLogin,
    onRoleChange,
    onIdInput,
    onPasswordInput
  };
});
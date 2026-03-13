import { defineComponent, ref, reactive } from '@vue-mini/core';
import { UserInfo, requireAuth, logout } from '@/utils/auth';
import { BASE_URL } from '@/app';

defineComponent(() => {
  const userInfo = ref<UserInfo | null>(null);
  const loading = ref(true);
  
  // 修改密码相关状态
  const showChangePassword = ref(false);
  const isChangingPassword = ref(false);
  const passwordError = ref('');
  
  // 修改密码表单数据
  const passwordForm = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });

  // 加载用户信息
  const loadUserInfo = async () => {
    try {
      const result = await requireAuth();
      if (result) {
        userInfo.value = result;
      }
    } catch (error) {
      console.error('加载用户信息失败:', error);
    } finally {
      loading.value = false;
    }
  };

  // 退出登录
  const handleLogout = () => {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
        }
      }
    });
  };

  // 页面显示时重新检查登录状态
  const onShow = () => {
    loadUserInfo();
  };

  // 显示修改密码模态框
  const showChangePasswordModal = () => {
    showChangePassword.value = true;
    passwordError.value = '';
  };

  // 隐藏修改密码模态框
  const hideChangePasswordModal = () => {
    showChangePassword.value = false;
    passwordForm.old_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
    passwordError.value = '';
  };

  // 处理原密码输入
  const onOldPasswordInput = (e: any) => {
    passwordForm.old_password = e.detail.value;
  };

  // 处理新密码输入
  const onNewPasswordInput = (e: any) => {
    passwordForm.new_password = e.detail.value;
  };

  // 处理确认密码输入
  const onConfirmPasswordInput = (e: any) => {
    passwordForm.confirm_password = e.detail.value;
  };

  // 处理修改密码
  const handleChangePassword = async () => {
    if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      passwordError.value = '请填写完整信息';
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      passwordError.value = '两次输入的新密码不一致';
      return;
    }

    if (passwordForm.new_password.length < 6) {
      passwordError.value = '新密码长度不能少于6位';
      return;
    }

    isChangingPassword.value = true;
    passwordError.value = '';

    try {
      const token = wx.getStorageSync('token');
      
      wx.request({
        url: `${BASE_URL}/change-password`,
        method: 'POST',
        data: {
          token,
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        },
        header: {
          'content-type': 'application/json'
        },
        success: (res) => {
          if (res.statusCode === 200) {
            wx.showToast({
              title: '密码修改成功',
              icon: 'success'
            });
            hideChangePasswordModal();
          } else {
            passwordError.value = '密码修改失败，请检查原密码是否正确';
          }
        },
        fail: (error) => {
          console.error('修改密码失败:', error);
          passwordError.value = '网络错误，请重试';
        },
        complete: () => {
          isChangingPassword.value = false;
        }
      });
    } catch (error) {
      console.error('修改密码异常:', error);
      passwordError.value = '修改失败，请重试';
      isChangingPassword.value = false;
    }
  };

  // 页面加载时检查登录状态
  const onLoad = () => {
    loadUserInfo();
  };

  return {
    userInfo,
    loading,
    showChangePassword,
    isChangingPassword,
    passwordError,
    passwordForm,
    handleLogout,
    onShow,
    onLoad,
    showChangePasswordModal,
    hideChangePasswordModal,
    onOldPasswordInput,
    onNewPasswordInput,
    onConfirmPasswordInput,
    handleChangePassword
  };
});
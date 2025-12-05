import { defineComponent, ref } from '@vue-mini/core';
import { UserInfo, requireAuth, logout } from '@/utils/auth';

defineComponent(() => {
  const userInfo = ref<UserInfo | null>(null);
  const loading = ref(true);

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

  // 页面加载时检查登录状态
  const onLoad = () => {
    loadUserInfo();
  };

  return {
    userInfo,
    loading,
    handleLogout,
    onShow,
    onLoad
  };
});
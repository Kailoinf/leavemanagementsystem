import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app';
import { requireAuth } from '@/utils/auth';

interface Reviewer {
  reviewer_id: number;
  name: string;
  role: string;
  school: string;
}

export default defineComponent(() => {
  const reviewers = ref<Reviewer[]>([]);
  const loading = ref(false);
  const page = ref(1);
  const pageSize = 20;
  const total = ref(0);
  const totalPages = ref(0);

  // 获取审核员数据
  const fetchReviewers = (isRefresh = false) => {
    if (isRefresh) {
      page.value = 1;
      reviewers.value = [];
    }

    loading.value = true;
    wx.showLoading({
      title: '加载中...',
    });

    const token = wx.getStorageSync('token');
    wx.request({
      url: BASE_URL + '/reviewers',
      method: 'GET',
      data: {
        token,
        page: page.value,
        page_size: pageSize
      },
      success: (res) => {
        console.log('审核员API返回数据:', res.data);
        const data = res.data as any;

        // 处理分页响应格式
        let reviewersData = [];
        if (data && data.items && Array.isArray(data.items)) {
          // 新的分页格式: {items: [...], total: X, page: Y, page_size: Z, total_pages: W}
          reviewersData = data.items;
          total.value = data.total || 0;
          totalPages.value = data.total_pages || 0;
        } else if (data && Array.isArray(data)) {
          // 直接返回数组（向后兼容）
          reviewersData = data;
        } else if (data && data.list && Array.isArray(data.list)) {
          // 返回包含list的对象（向后兼容）
          reviewersData = data.list;
        } else if (data && typeof data === 'object' && !Array.isArray(data)) {
          // 返回单个对象，包装成数组（向后兼容）
          reviewersData = [data];
        }

        console.log('处理后的审核员数据:', reviewersData);
        console.log('分页信息:', { page: page.value, total: total.value, totalPages: totalPages.value });

        if (isRefresh) {
          reviewers.value = reviewersData;
        } else {
          reviewers.value = [...reviewers.value, ...reviewersData];
        }
        wx.stopPullDownRefresh();
      },
      fail: (error) => {
        console.error('获取审核员数据失败:', error);
        wx.showToast({
          title: '加载失败',
          icon: 'error'
        });
        wx.stopPullDownRefresh();
      },
      complete: () => {
        loading.value = false;
        wx.hideLoading();
      }
    });
  };

  // 加载更多数据
  const loadMore = () => {
    if (!loading.value) {
      // 检查是否还有更多页面
      if (totalPages.value === 0 || page.value < totalPages.value) {
        page.value++;
        fetchReviewers();
      } else {
        console.log('没有更多数据了');
      }
    }
  };

  // 刷新数据
  const refreshData = () => {
    fetchReviewers(true);
  };

  // 下拉刷新
  const onPullDownRefresh = () => {
    fetchReviewers(true);
  };

  // 返回上一页
  const goBack = () => {
    wx.navigateBack();
  };

  // 检查登录状态并获取数据
  const initializePage = async () => {
    const userInfo = await requireAuth();
    if (userInfo) {
      console.log('页面加载完成，自动获取数据');
      fetchReviewers(true);
    }
  };

  // 页面加载时获取数据
  const onReady = () => {
    initializePage();
  };

  return {
    reviewers,
    loading,
    total,
    totalPages,
    page,
    fetchReviewers,
    loadMore,
    refreshData,
    onPullDownRefresh,
    goBack,
    onReady
  };
});
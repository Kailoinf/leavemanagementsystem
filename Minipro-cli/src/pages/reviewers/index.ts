import { defineComponent, ref } from '@vue-mini/core';

interface Reviewer {
  reviewer_id: number;
  name: string;
  role: string;
  department: string;
}

export default defineComponent(() => {
  const reviewers = ref<Reviewer[]>([]);
  const loading = ref(false);
  const page = ref(1);
  const pageSize = 20;

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

    wx.request({
      url: 'http://localhost:8000/reviewers',
      method: 'GET',
      data: {
        page: page.value,
        page_size: pageSize
      },
      success: (res) => {
        console.log('审核员API返回数据:', res.data);
        const data = res.data as any;

        // 处理不同的返回格式
        let reviewersData = [];
        if (data && Array.isArray(data)) {
          // 直接返回数组
          reviewersData = data;
        } else if (data && data.list && Array.isArray(data.list)) {
          // 返回包含list的对象
          reviewersData = data.list;
        } else if (data && typeof data === 'object' && !Array.isArray(data)) {
          // 返回单个对象，包装成数组
          reviewersData = [data];
        }

        console.log('处理后的审核员数据:', reviewersData);

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
      page.value++;
      fetchReviewers();
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

  // 页面加载时获取数据
  const onReady = () => {
    fetchReviewers(true);
  };

  return {
    reviewers,
    loading,
    fetchReviewers,
    loadMore,
    refreshData,
    onPullDownRefresh,
    goBack,
    onReady
  };
});
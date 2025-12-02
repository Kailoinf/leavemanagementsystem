import { defineComponent, ref } from '@vue-mini/core';

interface Leave {
  leave_id: number;
  student_id: string;
  leave_type: string;
  leave_days: number;
  leave_date: string;
  status: string;
  reviewer_id: string;
  audit_remarks: string;
  remarks: string;
  leave_date_formatted?: string;
}

export default defineComponent(() => {
  const leaves = ref<Leave[]>([]);
  const loading = ref(false);
  const page = ref(1);
  const pageSize = 20;

  // 格式化日期显示
  const formatDate = (dateStr: string): string => {
    if (!dateStr) return '';

    // 解析ISO日期字符串
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr; // 如果解析失败，返回原始字符串

    const now = new Date();
    const currentYear = now.getFullYear();
    const dateYear = date.getFullYear();

    if (dateYear === currentYear) {
      // 本年只显示月日
      const month = date.getMonth() + 1;
      const day = date.getDate();
      return `${month}月${day}日`;
    } else {
      // 非本年显示年月日
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const day = date.getDate();
      return `${year}年${month}月${day}日`;
    }
  };

  // 获取请假数据
  const fetchLeaves = (isRefresh = false) => {
    if (isRefresh) {
      page.value = 1;
      leaves.value = [];
    }

    loading.value = true;
    wx.showLoading({
      title: '加载中...',
    });

    wx.request({
      url: 'http://localhost:8000/leaves',
      method: 'GET',
      data: {
        page: page.value,
        page_size: pageSize
      },
      success: (res) => {
        console.log('请假API返回数据:', res.data);
        const data = res.data as any;

        // 处理不同的返回格式
        let leavesData = [];
        if (data && Array.isArray(data)) {
          // 直接返回数组
          leavesData = data;
        } else if (data && data.list && Array.isArray(data.list)) {
          // 返回包含list的对象
          leavesData = data.list;
        } else if (data && typeof data === 'object' && !Array.isArray(data)) {
          // 返回单个对象，包装成数组
          leavesData = [data];
        }

        console.log('处理后的请假数据:', leavesData);

        // 格式化日期字段
        const formattedLeavesData = leavesData.map((leave: any) => ({
          ...leave,
          leave_date_formatted: formatDate(leave.leave_date)
        }));

        if (isRefresh) {
          leaves.value = formattedLeavesData;
        } else {
          leaves.value = [...leaves.value, ...formattedLeavesData];
        }
        wx.stopPullDownRefresh();
      },
      fail: (error) => {
        console.error('获取请假数据失败:', error);
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
      fetchLeaves();
    }
  };


  // 下拉刷新
  const onPullDownRefresh = () => {
    fetchLeaves(true);
  };

  // 返回上一页
  const goBack = () => {
    wx.navigateBack();
  };

  // 页面加载时获取数据
  const onReady = () => {
    fetchLeaves(true);
  };

  return {
    leaves,
    loading,
    fetchLeaves,
    loadMore,
    onPullDownRefresh,
    goBack,
    onReady
  };
});
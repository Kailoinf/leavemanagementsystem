import { defineComponent, ref } from '@vue-mini/core';

interface Student {
  id?: number;
  student_id: string;
  name: string;
  department: string;
  reviewer_id: string;
  guarantee_permission: string;
  guarantee_permission_formatted?: string;
}

export default defineComponent(() => {
  const students = ref<Student[]>([]);
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

  // 获取学生数据
  const fetchStudents = (isRefresh = false) => {
    if (isRefresh) {
      page.value = 1;
      students.value = [];
    }

    loading.value = true;
    wx.showLoading({
      title: '加载中...',
    });

    wx.request({
      url: 'http://localhost:8000/students',
      method: 'GET',
      data: {
        page: page.value,
        page_size: pageSize
      },
      success: (res) => {
        console.log('学生API返回数据:', res.data);
        const data = res.data as any;

        // 处理不同的返回格式
        let studentsData = [];
        if (data && Array.isArray(data)) {
          // 直接返回数组
          studentsData = data;
        } else if (data && data.list && Array.isArray(data.list)) {
          // 返回包含list的对象
          studentsData = data.list;
        } else if (data && typeof data === 'object' && !Array.isArray(data)) {
          // 返回单个对象，包装成数组
          studentsData = [data];
        }

        console.log('处理后的学生数据:', studentsData);

        // 格式化日期字段
        const formattedStudentsData = studentsData.map((student: any) => ({
          ...student,
          guarantee_permission_formatted: formatDate(student.guarantee_permission)
        }));

        if (isRefresh) {
          students.value = formattedStudentsData;
        } else {
          students.value = [...students.value, ...formattedStudentsData];
        }
        wx.stopPullDownRefresh();
      },
      fail: (error) => {
        console.error('获取学生数据失败:', error);
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
      fetchStudents();
    }
  };

  // 刷新数据
  const refreshData = () => {
    fetchStudents(true);
  };

  // 下拉刷新
  const onPullDownRefresh = () => {
    fetchStudents(true);
  };

  // 返回上一页
  const goBack = () => {
    wx.navigateBack();
  };

  // 页面加载时获取数据
  const onReady = () => {
    fetchStudents(true);
  };

  return {
    students,
    loading,
    fetchStudents,
    loadMore,
    refreshData,
    onPullDownRefresh,
    goBack,
    onReady
  };
});
import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app'

export default defineComponent(() => {
    const studentCount = ref(0);
    const leaveCount = ref(0);
    const reviewerCount = ref(0);

    // 获取学生数量
    const getStudentCount = () => {
        console.log('获取学生数量');
        wx.request({
            url: BASE_URL + '/students/count',
            method: 'GET',
            success: (res) => {
                console.log('学生数量获取成功:', res.data);
                const data = res.data as any;
                studentCount.value = data?.students_count ?? data ?? 0;
            },
            fail: (error) => {
                console.error('学生数量获取失败:', error);
                studentCount.value = 0;
            }
        });
    };

    // 获取请假条数量
    const getLeaveCount = () => {
        console.log('获取请假条数量');
        wx.request({
            url: BASE_URL + '/leaves/count',
            method: 'GET',
            success: (res) => {
                console.log('请假条数量获取成功:', res.data);
                const data = res.data as any;
                leaveCount.value = data?.leaves_count ?? data?.count ?? data ?? 0;
            },
            fail: (error) => {
                console.error('请假条数量获取失败:', error);
                leaveCount.value = 0;
            }
        });
    };

    // 获取审核员数量
    const getReviewerCount = () => {
        console.log('获取审核员数量');
        wx.request({
            url: BASE_URL + '/reviewers/count',
            method: 'GET',
            success: (res) => {
                console.log('审核员数量获取成功:', res.data);
                const data = res.data as any;
                reviewerCount.value = data?.reviewers_count ?? data?.count ?? data ?? 0;
            },
            fail: (error) => {
                console.error('审核员数量获取失败:', error);
                reviewerCount.value = 0;
            }
        });
    };

    // 获取所有数据
    const getAllData = () => {
        getStudentCount();
        getLeaveCount();
        getReviewerCount();
    };

    // 页面加载时自动获取数据
    const onReady = () => {
        console.log('页面加载完成，自动获取数据');
        getAllData();
    };

    // 跳转到学生详情页面
    const goToStudents = () => {
        wx.navigateTo({
            url: '/pages/students/index'
        });
    };

    // 跳转到请假条详情页面
    const goToLeaves = () => {
        wx.navigateTo({
            url: '/pages/leaves/index'
        });
    };

    // 跳转到审核员详情页面
    const goToReviewers = () => {
        wx.navigateTo({
            url: '/pages/reviewers/index'
        });
    };

    return {
        studentCount,
        leaveCount,
        reviewerCount,
        getAllData,
        onReady,
        goToStudents,
        goToLeaves,
        goToReviewers
    };
});



import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app'

export default defineComponent(() => {
    const studentCount = ref(0);
    const leaveCount = ref(0);
    const reviewerCount = ref(0);
    const teacherCount = ref(0);
    const courseCount = ref(0);

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

    const getTeacherCount = () => {
        console.log('获取教师数量');
        wx.request({
            url: BASE_URL + '/teachers/count',
            method: 'GET',
            success: (res) => {
                console.log('教师数量获取成功:', res.data);
                const data = res.data as any;
                teacherCount.value = data?.teachers_count ?? data?.count ?? data ?? 0;
            },
            fail: (error) => {
                console.error('教师数量获取失败:', error);
                teacherCount.value = 0;
            }
        });
    };

    const getCourseCount = () => {
        console.log('获取课程数量');
        wx.request({
            url: BASE_URL + '/courses/count',
            method: 'GET',
            success: (res) => {
                console.log('课程数量获取成功:', res.data);
                const data = res.data as any;
                courseCount.value = data?.courses_count ?? data?.count ?? data ?? 0;
            },
            fail: (error) => {
                console.error('课程数量获取失败:', error);
                courseCount.value = 0;
            }
        })
    }
    // 获取所有数据
    const getAllData = () => {
        getStudentCount();
        getLeaveCount();
        getReviewerCount();
        getTeacherCount();
        getCourseCount();
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
    // 跳转到教师详情页面
    const goToTeachers = () => {
        wx.navigateTo({
            url: '/pages/teachers/index'
        });
    };
    // 跳转到课程详情页面
    const goToCourses = () => {
        wx.navigateTo({
            url: '/pages/courses/index'
        });
    };

    const scanCode = () => {
        wx.scanCode({
            success: (res) => {
                console.log('扫码成功:', res);
            },
        });
    };

    return {
        studentCount,
        leaveCount,
        reviewerCount,
        teacherCount,
        courseCount,
        getAllData,
        onReady,
        goToStudents,
        goToLeaves,
        goToReviewers,
        goToTeachers,
        goToCourses,
        scanCode,
    };
});



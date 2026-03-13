import { defineComponent, ref } from '@vue-mini/core';
import { BASE_URL } from '@/app';
import { requireAuth } from '@/utils/auth';

export default defineComponent(() => {
    const leaveCount = ref(0);

    

    // 获取请假条数量
    const getLeaveCount = () => {
        console.log('获取请假条数量');
        const token = wx.getStorageSync('token');
        wx.request({
            url: BASE_URL + '/leaves/count',
            method: 'GET',
            data: { token },
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

    
    // 检查登录状态并获取数据
    const initializePage = async () => {
        const userInfo = await requireAuth();
        if (userInfo) {
            console.log('页面加载完成，自动获取数据');
            getLeaveCount();
        }
    };

    // 页面加载时自动获取数据
    const onReady = () => {
        initializePage();
    };

    // 页面显示时检查登录状态
    const onShow = () => {
        initializePage();
    };

    // 扫一扫功能
    const scanCode = () => {
        wx.scanCode({
            success: (res) => {
                const token = wx.getStorageSync('token');
                const loginToken = res.result; // 扫码结果作为 login_token

                wx.request({
                    url: `${BASE_URL}/login/orcode`,
                    method: 'GET',
                    data: {
                        token: token,
                        login_token: loginToken
                    },
                    success: (response) => {
                        console.log('二维码登录成功:', response.data);
                        wx.showToast({
                            title: '登录成功',
                            icon: 'success'
                        });
                    },
                    fail: (error) => {
                        console.error('二维码登录失败:', error);
                        wx.showToast({
                            title: '登录失败',
                            icon: 'error'
                        });
                    }
                });
            },
            fail: (error) => {
                console.error('扫码失败:', error);
                wx.showToast({
                    title: '扫码失败',
                    icon: 'error'
                });
            }
        });
    };

    // 跳转到请假条页面
    const goToLeaves = () => {
        wx.navigateTo({
            url: '/pages/leaves/index'
        });
    };

    

    return {
        leaveCount,
        getLeaveCount,
        onReady,
        onShow,
        goToLeaves,
        scanCode,
    };
});



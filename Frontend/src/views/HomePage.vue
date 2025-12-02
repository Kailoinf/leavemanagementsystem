<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getData } from '../api'

const router = useRouter()

const studentResponse = ref<any>(null)
const leaveResponse = ref<any>(null)
const reviewerResponse = ref<any>(null)
const error = ref<string>('')

// 获取学生数量
const getStudentCount = async () => {
  try {
    const result = await getData('/students/count')
    studentResponse.value = result
    console.log('获取学生数量成功:', result)
  } catch (err: any) {
    error.value = err.message || '获取学生数量失败'
    console.error('获取学生数量错误:', err)
  }
}

// 获取请假条数量
const getLeavesCount = async () => {
  try {
    const result = await getData('/leaves/count')
    leaveResponse.value = result
    console.log('获取请假条数量成功:', result)
  } catch (err: any) {
    error.value = err.message || '获取请假条数量失败'
    console.error('获取请假条数量错误:', err)
  }
}
const getReviewerCount = async () => {
  try {
    const result = await getData('/reviewers/count')
    reviewerResponse.value = result
    console.log('获取审核员数量成功:', result)
  } catch (err: any) {
    error.value = err.message || '获取审核员数量失败'
    console.error('获取审核员数量错误:', err)
  }
}

// 组件挂载时自动获取数据
onMounted(() => {
  getStudentCount()
  getLeavesCount()
  getReviewerCount()
})

// 修改导航到列表页面的方法，使用 Vue Router
const goToStudentsList = () => {
  router.push('/students')
}

const goToLeavesList = () => {
  router.push('/leaves')
}

// 添加跳转到审核员列表的方法
const goToReviewersList = () => {
  router.push('/reviewers')
}
</script>
<template>
  <div class="container">
    <h1 class="page-title">🎓 LMS 管理系统</h1>

    <div v-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>

    <div v-else class="button-grid">
      <button @click="goToStudentsList" class="dashboard-button btn-primary">
        <div class="button-icon">👨‍🎓</div>
        <div class="button-title">学生管理</div>
        <div class="button-count">{{ studentResponse?.students_count || 0 }}</div>
        <div class="button-description">查看所有学生信息</div>
      </button>

      <button @click="goToLeavesList" class="dashboard-button btn-secondary">
        <div class="button-icon">📄</div>
        <div class="button-title">请假条管理</div>
        <div class="button-count">{{ leaveResponse?.leaves_count || 0 }}</div>
        <div class="button-description">管理请假申请</div>
      </button>

      <button @click="goToReviewersList" class="dashboard-button btn-success">
        <div class="button-icon">👥</div>
        <div class="button-title">审核员管理</div>
        <div class="button-count">{{ reviewerResponse?.reviewers_count || 0 }}</div>
        <div class="button-description">管理审核人员</div>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 容器样式 */
.container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 页面标题 */
.page-title {
  color: white;
  font-size: 3rem;
  font-weight: 800;
  text-align: center;
  margin-bottom: 48px;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
  letter-spacing: 1px;
}

/* 按钮网格布局 */
.button-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 仪表板按钮样式 */
.dashboard-button {
  background: white;
  border: none;
  border-radius: 20px;
  padding: 32px 24px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.dashboard-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: height 0.3s ease;
}

.dashboard-button:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.dashboard-button:hover::before {
  height: 8px;
}

.dashboard-button:active {
  transform: translateY(-4px) scale(1.01);
}

/* 按钮变体 */
.btn-primary {
  border-top: 4px solid #667eea;
}

.btn-primary::before {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.btn-secondary {
  border-top: 4px solid #f093fb;
}

.btn-secondary::before {
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
}

.btn-success {
  border-top: 4px solid #28a745;
}

.btn-success::before {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
}

/* 按钮内容样式 */
.button-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
  text-align: center;
  animation: float 3s ease-in-out infinite;
}

.button-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  text-align: center;
}

.button-count {
  font-size: 2.5rem;
  font-weight: 800;
  color: #667eea;
  margin-bottom: 12px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.button-description {
  font-size: 0.9rem;
  color: #6c757d;
  text-align: center;
  line-height: 1.4;
  font-weight: 500;
}

/* 不同按钮类型的计数颜色 */
.btn-secondary .button-count {
  color: #f093fb;
  text-shadow: 0 2px 4px rgba(240, 147, 251, 0.2);
}

.btn-success .button-count {
  color: #28a745;
  text-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
}

/* 浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 错误状态 */
.error {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  font-weight: 600;
  border-radius: 16px;
  margin: 40px auto;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.error span {
  color: #dc3545;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .page-title {
    font-size: 2.2rem;
    margin-bottom: 32px;
  }

  .button-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .dashboard-button {
    padding: 24px 20px;
  }

  .button-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
  }

  .button-title {
    font-size: 1.3rem;
    margin-bottom: 6px;
  }

  .button-count {
    font-size: 2rem;
    margin-bottom: 10px;
  }

  .button-description {
    font-size: 0.85rem;
  }

  .dashboard-button:hover {
    transform: translateY(-6px) scale(1.01);
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
    margin-bottom: 24px;
  }

  .dashboard-button {
    padding: 20px 16px;
  }

  .button-icon {
    font-size: 2rem;
    margin-bottom: 8px;
  }

  .button-title {
    font-size: 1.1rem;
  }

  .button-count {
    font-size: 1.8rem;
  }
}
</style>
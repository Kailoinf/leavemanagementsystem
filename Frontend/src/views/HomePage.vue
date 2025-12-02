<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useApiCount } from '../composables/useApiData'
import { useNavigation } from '../composables/useNavigation'
import type { CountResponse } from '../types'

// 使用组合式函数
const { data: studentResponse, fetchCount: getStudentCount, error: studentError } = useApiCount<Record<string, number>>('/students/count')
const { data: leaveResponse, fetchCount: getLeavesCount, error: leaveError } = useApiCount<Record<string, number>>('/leaves/count')
const { data: reviewerResponse, fetchCount: getReviewerCount, error: reviewerError } = useApiCount<Record<string, number>>('/reviewers/count')

const { goToStudents, goToLeaves, goToReviewers } = useNavigation()

// 合并错误状态
const error = ref('')

// 更新导航方法名称
const goToStudentsList = () => {
  goToStudents()
}

const goToLeavesList = () => {
  goToLeaves()
}

const goToReviewersList = () => {
  goToReviewers()
}

// 组件挂载时自动获取数据
onMounted(() => {
  getStudentCount()
  getLeavesCount()
  getReviewerCount()
})
</script>
<template>
  <div class="container">
    <h1 class="page-title-home">🎓 LMS 管理系统</h1>

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
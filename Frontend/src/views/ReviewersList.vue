<script setup lang="ts">
import { onMounted } from 'vue'
import { useApiData } from '../composables/useApiData'
import { useNavigation } from '../composables/useNavigation'
import type { Reviewer } from '../types'

// 使用组合式函数
const { data: reviewers, loading, error, fetchData: fetchReviewers } = useApiData<Reviewer>('/reviewers/')
const { goToHome } = useNavigation()

// 组件挂载时获取数据
onMounted(() => {
  fetchReviewers()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">审核员列表</h1>
    <button @click="goToHome" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">👥 共 {{ reviewers.length }} 名审核员</p>
      </div>

      <div v-if="reviewers.length === 0" class="empty-state">
        <p>📋 暂无审核员数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>审核员ID</th>
              <th>姓名</th>
              <th>职务</th>
              <th>部门</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="reviewer in reviewers" :key="reviewer.reviewer_id">
              <td>{{ reviewer.reviewer_id }}</td>
              <td>{{ reviewer.name }}</td>
              <td>
                <span class="badge badge-primary">{{ reviewer.role }}</span>
              </td>
              <td>{{ reviewer.department }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
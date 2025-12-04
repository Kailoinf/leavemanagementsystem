<script setup lang="ts">
import { onMounted } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import { formatDate, getStatusBadgeClass } from '../utils/formatters'
import PaginationControls from '../components/PaginationControls.vue'
import type { Leave } from '../types'

// 使用分页组合式函数
const {
  data: leaves,
  loading,
  error,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData: fetchLeaves,
  goToPage,
  setPageSize
} = usePagedData<Leave>('/leaves')
const { goToHome } = useNavigation()

// 组件挂载时获取数据
onMounted(() => {
  fetchLeaves()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">请假条列表</h1>
    <button @click="goToHome" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">📄 共 {{ total }} 张请假条 (第 {{ currentPage }} / {{ totalPages }} 页)</p>
      </div>

      <div v-if="leaves.length === 0" class="empty-state">
        <p>📋 暂无请假条数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>请假ID</th>
                <th>学生ID</th>
                <th>请假类型</th>
                <th>请假天数</th>
                <th>请假时间</th>
                <th>状态</th>
                <th>审核人ID</th>
                <th>审核人姓名</th>
                <th>审核意见</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="leave in leaves" :key="leave.leave_id">
                <td>{{ leave.leave_id }}</td>
                <td>{{ leave.student_id }}</td>
                <td>{{ leave.leave_type }}</td>
                <td>{{ leave.leave_days }}</td>
                <td>{{ formatDate(leave.leave_date) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(leave.status)" class="badge">
                    {{ leave.status }}
                  </span>
                </td>
                <td>{{ leave.reviewer_id }}</td>
                <td>{{ leave.reviewer_name }}</td>
                <td>{{ leave.audit_remarks }}</td>
                <td>{{ leave.remarks }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页控件 -->
        <PaginationControls
          :current-page="currentPage"
          :total-pages="totalPages"
          :total="total"
          :page-size="pageSize"
          :loading="loading"
          @page-change="goToPage"
          @page-size-change="setPageSize"
        />
      </div>
    </div>
  </div>
</template>

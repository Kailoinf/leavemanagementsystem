<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getData } from '../api'

const students = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// 获取所有学生数据
const fetchStudents = async () => {
  loading.value = true
  try {
    const result = await getData('/students/')
    students.value = Array.isArray(result) ? result : []
    console.log('获取学生列表成功:', result)
  } catch (err: any) {
    error.value = err.message || '获取学生列表失败'
    console.error('获取学生列表错误:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">学生列表</h1>
    <button @click="$router.push('/')" class="btn btn-back">← 返回首页</button>

    <div v-if="loading" class="loading">
      <span>🔄 正在加载数据...</span>
    </div>
    <div v-else-if="error" class="error">
      <span>❌ {{ error }}</span>
    </div>
    <div v-else>
      <div class="stats-card">
        <p class="stats-text">📚 共 {{ students.length }} 名学生</p>
      </div>

      <div v-if="students.length === 0" class="empty-state">
        <p>📋 暂无学生数据</p>
        <p>请等待数据添加完成后再来查看</p>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>学号</th>
              <th>姓名</th>
              <th>院系</th>
              <th>审核人ID</th>
              <th>担保权限到期时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.student_id">
              <td>{{ student.student_id }}</td>
              <td>{{ student.name }}</td>
              <td>{{ student.department }}</td>
              <td>{{ student.reviewer_id }}</td>
              <td>{{ student.guarantee_permission }}</td>
            </tr>
          </tbody>
        </table>
      </div>
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 页面标题 */
.page-title {
  color: #2c3e50;
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 32px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 按钮样式 */
.btn {
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(240, 147, 251, 0.5);
}

.btn-back {
  background: linear-gradient(45deg, #6c757d 0%, #495057 100%);
  color: white;
  margin-bottom: 32px;
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.btn-back:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

/* 统计卡片 */
.stats-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stats-text {
  font-size: 1.2rem;
  color: #495057;
  font-weight: 600;
  text-align: center;
}

/* 数据表格 */
.table-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  padding: 16px;
  text-align: left;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 12px;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  color: #2c3e50;
  font-weight: 500;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover {
  background-color: rgba(102, 126, 234, 0.08);
  transition: background-color 0.3s ease;
}

.data-table tr:nth-child(even) {
  background-color: rgba(248, 249, 250, 0.5);
}

.data-table tr:nth-child(even):hover {
  background-color: rgba(102, 126, 234, 0.12);
}

/* 状态徽章 */
.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 加载和错误状态 */
.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  margin: 20px 0;
  background: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.loading {
  color: #667eea;
  background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.error {
  color: #dc3545;
  background: linear-gradient(45deg, rgba(220, 53, 69, 0.1), rgba(255, 73, 97, 0.1));
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.empty-state p {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 8px 0;
  font-weight: 500;
}

.empty-state p:first-child {
  font-size: 1.3rem;
  color: #495057;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .page-title {
    font-size: 2rem;
    margin-bottom: 24px;
  }

  .btn {
    padding: 10px 20px;
    font-size: 14px;
  }

  .data-table {
    font-size: 12px;
  }

  .data-table th,
  .data-table td {
    padding: 8px 12px;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>
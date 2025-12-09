<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePagedData } from '../composables/usePagedData'
import { useNavigation } from '../composables/useNavigation'
import { exportToExcel } from '../utils/excelExporter'
import PaginationControls from './PaginationControls.vue'

interface Props {
  endpoint: string
  title?: string
  columns: Array<{ key: string; label: string; formatter?: (value: any) => string }>
  icon?: string
  itemLabel: string
  showActions?: boolean
  customData?: any[]
  customLoading?: boolean
  customError?: string
  customTotal?: number
  hideExport?: boolean
  hideBackButton?: boolean
  backButtonText?: string
  onBackClick?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  icon: '',
  showActions: false,
  hideExport: false,
  hideBackButton: false
})

// 导出相关状态
const isExporting = ref(false)

// 使用自定义数据或从endpoint获取数据
const {
  data: fetchedData,
  loading: fetchedLoading,
  error: fetchedError,
  currentPage,
  total,
  totalPages,
  pageSize,
  fetchData,
  goToPage,
  setPageSize
} = props.customData ? {
  data: ref(props.customData),
  loading: ref(false),
  error: ref(''),
  currentPage: ref(1),
  total: ref(props.customData?.length || 0),
  totalPages: ref(1),
  pageSize: ref(10),
  fetchData: () => Promise.resolve(),
  goToPage: () => { },
  setPageSize: () => { }
} : usePagedData<any>(props.endpoint)

// 使用自定义数据或获取的数据
const data = computed(() => props.customData || fetchedData.value)
const loading = computed(() => props.customLoading !== undefined ? props.customLoading : fetchedLoading.value)
const error = computed(() => props.customError !== undefined ? props.customError : fetchedError.value)
const displayTotal = computed(() => props.customTotal !== undefined ? props.customTotal : total.value)

const { goToHome } = useNavigation()

// 导出CSV功能
const handleExportCSV = async () => {
  try {
    isExporting.value = true

    let allData: any[] = []

    // 如果是自定义数据，直接使用
    if (props.customData) {
      allData = props.customData
    } else {
      // 获取所有数据，不分页
      const token = localStorage.getItem('token')
      if (!token) {
        console.error('未找到 token，无法导出')
        return
      }

      console.log('正在获取所有数据用于导出...')

      let currentPage = 1
      let hasMoreData = true

      // 循环获取所有页面的数据
      while (hasMoreData) {
        const params = new URLSearchParams({
          token,
          page: currentPage.toString(),
          page_size: '100' // 设置为最大值100
        })

        const response = await fetch(`/api/v1${props.endpoint}?${params}`)
        if (!response.ok) {
          throw new Error(`导出失败: ${response.statusText}`)
        }

        const result = await response.json()
        const currentPageData = result.items || []

        // 将当前页数据添加到总数据中
        allData = allData.concat(currentPageData)

        console.log(`已获取第 ${currentPage} 页数据，本页 ${currentPageData.length} 条，累计 ${allData.length} 条`)

        // 检查是否还有下一页
        if (currentPageData.length < 100) {
          hasMoreData = false
        } else {
          currentPage++
        }
      }
    }

    if (allData.length === 0) {
      alert('没有数据可以导出')
      return
    }

    // 使用props.columns的顺序作为主要导出顺序
    const mainFieldNames = props.columns.map(col => col.key)

    // 获取columns中没有但存在于数据中的其他字段
    const additionalFields = new Set<string>()
    allData.forEach((item: any) => {
      Object.keys(item).forEach(key => {
        if (!mainFieldNames.includes(key)) {
          additionalFields.add(key)
        }
      })
    })

    // 合并字段名：先按照columns顺序，然后是其他字段
    const fieldNames = [...mainFieldNames, ...Array.from(additionalFields)]

    // 使用字段名作为列名（翻译为中文）
    const headers = fieldNames.map(field => {
      // 简单的字段名翻译，可以根据需要扩展
      const fieldTranslations: { [key: string]: string } = {
        'student_id': '学生ID',
        'student_name': '学生姓名',
        'teacher_id': '教师ID',
        'teacher_name': '教师姓名',
        'reviewer_id': '审核员ID',
        'reviewer_name': '审核员姓名',
        'admin_id': '管理员ID',
        'course_id': '课程ID',
        'course_name': '课程名称',
        'leave_id': '请假ID',
        'class_hours': '课时',
        'school': '院系/部门',
        'role': '职务',
        'password': '密码',
        'guarantee_permission': '担保权限到期时间',
        'enrollment_date': '选课日期',
        'status': '状态',
        'enrollment_count': '选课人数',
        'leave_type': '请假类型',
        'leave_hours': '请假课时',
        'leave_date': '请假日期',
        'remarks': '备注',
        'materials': '材料',
        'audit_remarks': '审核意见',
        'audit_time': '审核时间'
      }
      return fieldTranslations[field] || field
    })

    // 转换数据格式，按照指定顺序
    const csvData = allData.map((item: any) => {
      const row: any = {}
      fieldNames.forEach((fieldName, index) => {
        let value = item[fieldName]

        // 格式化日期字段
        if (value && (fieldName.includes('date') || fieldName.includes('time'))) {
          value = new Date(value).toLocaleString('zh-CN')
        }

        const headerName = headers[index]
        if (headerName) {
          row[headerName] = value || ''
        }
      })
      return row
    })

    // 导出为 Excel
    exportToExcel(csvData, props.title, headers)

  } catch (error: any) {
    console.error('导出失败:', error)
    alert(`导出失败: ${error.message || '未知错误'}`)
  } finally {
    isExporting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="list-page">
    <div class="container">
      <div class="page-header">
        <h1 v-if="title" class="page-title">{{ title }}</h1>
        <div class="header-buttons">
          <button v-if="!hideExport" @click="handleExportCSV" class="btn btn-export" :disabled="isExporting">
            {{ isExporting ? '导出中...' : '导出Excel' }}
          </button>
          <button v-if="!hideBackButton" @click="onBackClick ? onBackClick() : goToHome()" class="btn btn-back">
            {{ backButtonText || '返回首页' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>正在加载数据...</span>
      </div>
      <div v-else-if="error" class="error">
        <span>{{ error }}</span>
      </div>
      <div v-else class="page-content">
        <div class="stats-card">
          <p class="stats-text">共 {{ displayTotal }} {{ itemLabel }} (第 {{ currentPage }} / {{ totalPages }} 页)</p>
        </div>

        <div v-if="data.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>暂无{{ itemLabel }}数据</h3>
          <p>请等待数据添加完成后再来查看</p>
        </div>

        <div v-else class="data-section">
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
                  <th v-if="showActions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in data" :key="item.id || (columns[0] && item[columns[0].key])" class="table-row">
                  <template v-for="column in columns" :key="column.key">
                    <slot v-if="$slots['table-cell']" name="table-cell" :item="item" :column="column">
                      <td class="table-cell">
                        <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
                        <span v-else>{{ item[column.key] }}</span>
                      </td>
                    </slot>
                    <td v-else class="table-cell">
                      <span v-if="column.formatter">{{ column.formatter(item[column.key]) }}</span>
                      <span v-else>{{ item[column.key] }}</span>
                    </td>
                  </template>
                  <td v-if="showActions" class="table-cell">
                    <slot name="actions" :item="item"></slot>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页控件 (仅在非自定义数据时显示) -->
          <PaginationControls v-if="!props.customData" :current-page="currentPage" :total-pages="totalPages"
            :total="displayTotal" :page-size="pageSize" :loading="loading" @page-change="goToPage"
            @page-size-change="setPageSize" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-page {
  min-height: 100vh;
  background-color: var(--bg-secondary);
  padding: var(--spacing-lg) 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing);
  border-bottom: 1px solid var(--border-light);
}

.header-buttons {
  display: flex;
  gap: var(--spacing);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.btn-back {
  background-color: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
}

.btn-back:hover {
  background-color: var(--gray-200);
  color: var(--text-primary);
  border-color: var(--border-dark);
}

.btn-export {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.btn-export:hover {
  background-color: #059669;
  color: white;
}

.btn-export:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.7;
}

.page-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.stats-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: var(--spacing);
  box-shadow: var(--shadow);
}

.stats-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
  gap: var(--spacing);
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border-light);
  border-top: 2px solid var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--error);
  background-color: var(--error-light);
  border: 1px solid #fca5a5;
  border-radius: var(--radius-lg);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0;
}

.data-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.table-container {
  overflow-x: auto;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  background-color: var(--gray-50);
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 2px solid var(--border-medium);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table td {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.table-row {
  transition: background-color var(--transition-fast);
}

.table-row:hover {
  background-color: var(--gray-50);
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-cell {
  position: relative;
  vertical-align: middle;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .list-page {
    padding: var(--spacing) 0;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing);
    margin-bottom: var(--spacing-lg);
  }

  .page-title {
    font-size: var(--text-2xl);
    text-align: center;
  }

  .btn-back {
    align-self: center;
  }

  .data-table th,
  .data-table td {
    padding: 0.75rem 0.5rem;
    font-size: var(--text-xs);
  }

  .empty-state {
    padding: var(--spacing-lg);
  }

  .empty-icon {
    font-size: 2rem;
  }

  .empty-state h3 {
    font-size: var(--text-lg);
  }
}

@media (max-width: 480px) {
  .page-header {
    padding-bottom: var(--spacing-sm);
  }

  .page-title {
    font-size: var(--text-xl);
  }

  .data-table th,
  .data-table td {
    padding: 0.5rem 0.25rem;
  }

  .empty-state {
    padding: var(--spacing);
  }

  .empty-icon {
    font-size: 1.5rem;
  }

  .empty-state h3 {
    font-size: var(--text-base);
  }
}
</style>
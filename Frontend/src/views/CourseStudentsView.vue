<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GenericList from '../components/GenericList.vue'
import { getStatusBadgeClass } from '../utils/formatters'

// 获取路由参数
const router = useRouter()
const courseId = parseInt(useRoute().params.id as string)

// 返回课程列表页面
const goBackToCourses = () => {
  router.push('/courses')
}

// 数据状态
const students = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const courseName = ref('')

// 获取课程学生名单
const fetchCourseStudents = async () => {
  try {
    loading.value = true
    error.value = ''

    const token = localStorage.getItem('token')
    const response = await fetch(`/api/v1/student-courses/course/${courseId}?token=${token}`)
    if (!response.ok) {
      throw new Error(`获取数据失败: ${response.statusText}`)
    }

    const data = await response.json()
    students.value = data

    // 从第一个学生的记录中获取课程名称
    if (data.length > 0 && data[0]?.course_name) {
      courseName.value = data[0].course_name
    } else {
      courseName.value = `课程 ${courseId}`
    }

    console.log(`课程 ${courseId} 的学生名单:`, students.value)
  } catch (err: any) {
    console.error('获取课程学生名单失败:', err)
    error.value = '获取课程学生名单失败，请重试'
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  if (courseId) {
    fetchCourseStudents()
  } else {
    error.value = '无效的课程ID'
  }
})

</script>

<template>
  <div class="course-students-page">
    <GenericList
      endpoint="/dummy"
      :custom-data="students"
      :custom-loading="loading"
      :custom-error="error"
      :custom-total="students.length"
      :title="`${courseName} - 学生名单`"
      :columns="[
        { key: 'student_id', label: '学生ID' },
        { key: 'student_name', label: '学生姓名' },
        { key: 'course_name', label: '课程名称' },
        { key: 'teacher_name', label: '教师姓名' },
        { key: 'enrollment_date', label: '选课日期' },
        { key: 'status', label: '状态' }
      ]"
      item-label="名学生"
      :show-actions="false"
      :hide-back-button="false"
      :hide-export="false"
      back-button-text="返回课程列表"
      :on-back-click="goBackToCourses"
    >
      <template #table-cell="{ item, column }">
        <td v-if="column.key === 'status'" class="table-cell">
          <span :class="getStatusBadgeClass(item.status)" class="badge">
            {{ item.status }}
          </span>
        </td>
        <td v-else class="table-cell">
          {{ item[column.key] || '未知' }}
        </td>
      </template>
    </GenericList>
  </div>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
</style>
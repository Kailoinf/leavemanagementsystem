<script setup lang="ts">
import { useRouter } from 'vue-router'
import GenericList from '../components/GenericList.vue'

const router = useRouter()

// 获取当前用户角色
const currentUserRole = localStorage.getItem('role') || ''

// 跳转到课程学生名单页面
const goToCourseStudents = (courseId: number) => {
  router.push(`/courses/${courseId}/students`)
}

</script>

<template>
  <GenericList
    endpoint="/courses"
    title="课程列表"
    :show-actions="currentUserRole !== 'student'"
    :columns="[
      { key: 'course_id', label: '课程ID' },
      { key: 'course_name', label: '课程名称' },
      { key: 'class_hours', label: '课时' },
      { key: 'teacher_name', label: '教师姓名' },
      {
        key: 'enrollment_count',
        label: '选课人数',
        formatter: (value: any) => `${value || 0} 人`
      }
    ]"
    item-label="门课程"
  >
    <template #actions="{ item }">
      <button @click="goToCourseStudents(item.course_id)" class="btn btn-primary btn-sm">
        查看学生名单
      </button>
    </template>
  </GenericList>
</template>


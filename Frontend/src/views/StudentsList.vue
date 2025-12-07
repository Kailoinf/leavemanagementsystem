<script setup lang="ts">
import GenericList from '../components/GenericList.vue'
import { formatDate } from '../utils/formatters'
</script>

<template>
  <GenericList
    endpoint="/students"
    title="学生列表"
    :columns="[
      { key: 'student_id', label: '学号' },
      { key: 'name', label: '姓名' },
      { key: 'school', label: '院系' },
      { key: 'reviewer_id', label: '审核人ID' },
      { key: 'reviewer_name', label: '审核人姓名' },
      { key: 'guarantee_permission', label: '担保权限到期时间', formatter: formatDate }
    ]"
    itemLabel="名学生"
  />
</template>
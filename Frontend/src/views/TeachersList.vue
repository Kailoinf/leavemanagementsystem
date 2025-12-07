<script setup lang="ts">
import GenericList from '../components/GenericList.vue'
</script>

<template>
  <GenericList
    endpoint="/teachers"
    title="教师列表"
    :columns="[
      { key: 'teacher_id', label: '教师ID' },
      { key: 'name', label: '姓名' },
      { key: 'password', label: '密码' }
    ]"
    item-label="名教师"
  />
</template>
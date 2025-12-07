<script setup lang="ts">
import GenericList from '../components/GenericList.vue'
</script>

<template>
  <GenericList
    endpoint="/reviewers"
    title="审核员列表"
    :columns="[
      { key: 'reviewer_id', label: '审核员ID' },
      { key: 'name', label: '姓名' },
      { key: 'role', label: '职务' },
      { key: 'school', label: '部门' }
    ]"
    itemLabel="名审核员"
  />
</template>
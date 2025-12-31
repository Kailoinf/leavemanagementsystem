<script setup lang="ts">
import { ref, computed } from 'vue'
import GenericList from '../components/GenericList.vue'
import ChangePasswordModal from '../components/ChangePasswordModal.vue'

// 当前用户角色
const currentUserRole = computed(() => localStorage.getItem('role'))

// 是否为管理员
const isAdmin = computed(() => currentUserRole.value === 'admin')

// 修改密码模态框状态
const showPasswordModal = ref(false)
const selectedUser = ref<{ id: number; name: string } | null>(null)

// 打开修改密码模态框
const openChangePassword = (item: any) => {
  selectedUser.value = {
    id: item.reviewer_id,
    name: item.reviewer_name
  }
  showPasswordModal.value = true
}

// 关闭修改密码模态框
const closePasswordModal = () => {
  showPasswordModal.value = false
  selectedUser.value = null
}

// 修改密码成功回调
const onPasswordChanged = () => {
  // 可以显示成功消息或刷新列表
  console.log('密码修改成功')
}
</script>

<template>
  <div>
    <GenericList endpoint="/reviewers" title="审核员列表" :columns="[
      { key: 'reviewer_id', label: '审核员ID' },
      { key: 'reviewer_name', label: '姓名' },
      { key: 'role_name', label: '职务' },
      { key: 'school_name', label: '院系' }
    ]" item-label="名审核员" :show-actions="isAdmin">
      <template #actions="{ item }">
        <button v-if="isAdmin" @click="openChangePassword(item)" class="btn btn-sm btn-outline" title="修改密码">
          修改密码
        </button>
      </template>
    </GenericList>

    <!-- 修改密码模态框 -->
    <ChangePasswordModal :show="showPasswordModal" :user-id="selectedUser?.id" :user-name="selectedUser?.name"
      @close="closePasswordModal" @success="onPasswordChanged" />
  </div>
</template>

<style scoped>
.btn {
  padding: 0.25rem 0.5rem;
  font-size: var(--text-xs);
  border-radius: var(--radius);
  border: 1px solid var(--border-medium);
  background-color: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition);
}

.btn:hover {
  background-color: var(--gray-100);
  color: var(--text-primary);
  border-color: var(--border-dark);
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}

.btn-outline {
  border: 1px solid var(--border-medium);
}
</style>
<script setup lang="ts">
import { ref } from 'vue'
import { changePassword, changeUserPassword } from '../api/index'

interface Props {
  show: boolean
  userId?: number  // 如果提供，则为管理员修改指定用户密码
  userName?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: []
}>()

// 表单数据
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

// 关闭模态框
const handleClose = () => {
  if (!loading.value) {
    emit('close')
    // 重置表单
    passwordForm.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    }
    error.value = ''
    success.value = ''
  }
}

// 修改密码
const handleSubmit = async () => {
  // 验证表单
  if (!passwordForm.value.old_password || !passwordForm.value.new_password || !passwordForm.value.confirm_password) {
    error.value = '请填写所有字段'
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    error.value = '新密码和确认密码不一致'
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    error.value = '新密码长度不能少于6位'
    return
  }

  try {
    loading.value = true
    error.value = ''
    success.value = ''

    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未找到认证令牌')
    }

    if (props.userId) {
      // 管理员修改指定用户密码
      await changeUserPassword(props.userId, {
        old_password: passwordForm.value.old_password,
        new_password: passwordForm.value.new_password
      }, token)
    } else {
      // 用户修改自己的密码
      await changePassword({
        old_password: passwordForm.value.old_password,
        new_password: passwordForm.value.new_password
      }, token)
    }

    success.value = '密码修改成功！'

    // 1秒后关闭模态框并触发成功事件
    setTimeout(() => {
      emit('success')
      emit('close')
    }, 1000)

  } catch (error: any) {
    error.value = error.response?.data?.detail || error.message || '修改密码失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>修改密码</h3>
        <button @click="handleClose" class="modal-close" :disabled="loading">×</button>
      </div>

      <div class="modal-body">
        <!-- 提示信息 -->
        <div v-if="userName" class="info-text">
          正在为用户 <strong>{{ userName }}</strong> 修改密码
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- 成功信息 -->
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="old_password">当前密码</label>
            <input type="password" id="old_password" v-model="passwordForm.old_password" class="form-input"
              placeholder="请输入当前密码" required :disabled="loading" />
          </div>

          <div class="form-group">
            <label for="new_password">新密码</label>
            <input type="password" id="new_password" v-model="passwordForm.new_password" class="form-input"
              placeholder="请输入新密码（至少6位）" minlength="6" required :disabled="loading" />
          </div>

          <div class="form-group">
            <label for="confirm_password">确认新密码</label>
            <input type="password" id="confirm_password" v-model="passwordForm.confirm_password" class="form-input"
              placeholder="请再次输入新密码" minlength="6" required :disabled="loading" />
          </div>

          <div class="form-actions">
            <button type="button" @click="handleClose" class="btn btn-outline" :disabled="loading">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  transition: all var(--transition);
}

.modal-close:hover:not(:disabled) {
  color: var(--text-primary);
  background-color: var(--gray-100);
}

.modal-close:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.modal-body {
  padding: var(--spacing-xl);
}

.info-text {
  background-color: var(--blue-50);
  color: var(--blue-700);
  padding: var(--spacing);
  border-radius: var(--radius);
  margin-bottom: var(--spacing);
  font-size: var(--text-sm);
}

.form-group {
  margin-bottom: var(--spacing);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius);
  font-size: var(--text-base);
  transition: border-color var(--transition);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background-color: var(--gray-50);
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: var(--spacing);
  justify-content: flex-end;
  margin-top: var(--spacing-xl);
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
  cursor: pointer;
  border: none;
  font-size: var(--text-sm);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary-500);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-600);
}

.btn-outline {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--gray-100);
  color: var(--text-primary);
}

.alert {
  padding: var(--spacing);
  border-radius: var(--radius);
  margin-bottom: var(--spacing);
  font-size: var(--text-sm);
}

.alert-danger {
  background-color: var(--red-50);
  color: var(--red-700);
  border: 1px solid var(--red-200);
}

.alert-success {
  background-color: var(--green-50);
  color: var(--green-700);
  border: 1px solid var(--green-200);
}
</style>
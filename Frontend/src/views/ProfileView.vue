<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { changePassword } from '../api/index'
import GenericList from '../components/GenericList.vue'

const router = useRouter()

// 用户信息
const userInfo = ref({
  id: '',
  name: '',
  role: ''
})

// 修改密码表单
const showPasswordModal = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// 角色中文映射
const roleMap: { [key: string]: string } = {
  admin: '管理员',
  reviewer: '审核员',
  teacher: '教师',
  student: '学生'
}

// 获取用户信息
const getUserInfo = () => {
  const id = localStorage.getItem('id')
  const name = localStorage.getItem('name')
  const role = localStorage.getItem('role')

  if (id && name && role) {
    userInfo.value = { id, name, role }
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 退出登录
const logout = () => {
  localStorage.clear()
  router.push('/login')
}

// 打开修改密码模态框
const openPasswordModal = () => {
  showPasswordModal.value = true
  passwordError.value = ''
  passwordSuccess.value = ''
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 关闭修改密码模态框
const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 修改密码
const handleChangePassword = async () => {
  // 验证表单
  if (!passwordForm.value.old_password || !passwordForm.value.new_password || !passwordForm.value.confirm_password) {
    passwordError.value = '请填写所有字段'
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = '新密码和确认密码不一致'
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    passwordError.value = '新密码长度不能少于6位'
    return
  }

  try {
    passwordLoading.value = true
    passwordError.value = ''
    passwordSuccess.value = ''

    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('未找到认证令牌')
    }

    await changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    }, token)

    passwordSuccess.value = '密码修改成功！'

    // 2秒后关闭模态框
    setTimeout(() => {
      closePasswordModal()
    }, 2000)

  } catch (error: any) {
    passwordError.value = error.response?.data?.detail || error.message || '修改密码失败'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  getUserInfo()
})
</script>

<template>
  <div class="profile-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">个人资料</h1>
        <div class="header-buttons">
          <button @click="goHome" class="btn btn-back">返回首页</button>
          <button @click="logout" class="btn btn-logout">退出登录</button>
        </div>
      </div>

      <!-- 用户信息卡片 -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar">
            <span class="avatar-text">{{ userInfo.name?.charAt(0) || 'U' }}</span>
          </div>
          <h2 class="user-name">{{ userInfo.name }}</h2>
          <span class="user-role">{{ roleMap[userInfo.role] || userInfo.role }}</span>
        </div>

        <div class="profile-info">
          <div class="info-item">
            <label>用户ID</label>
            <span>{{ userInfo.id }}</span>
          </div>
          <div class="info-item">
            <label>角色</label>
            <span>{{ roleMap[userInfo.role] || userInfo.role }}</span>
          </div>
          <div class="info-item">
            <label>姓名</label>
            <span>{{ userInfo.name }}</span>
          </div>
        </div>

        <div class="profile-actions">
          <button @click="openPasswordModal" class="btn btn-primary">
            修改密码
          </button>
        </div>
      </div>
    </div>

    <!-- 修改密码模态框 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button @click="closePasswordModal" class="modal-close">×</button>
        </div>

        <div class="modal-body">
          <!-- 错误信息 -->
          <div v-if="passwordError" class="alert alert-danger">
            {{ passwordError }}
          </div>

          <!-- 成功信息 -->
          <div v-if="passwordSuccess" class="alert alert-success">
            {{ passwordSuccess }}
          </div>

          <form @submit.prevent="handleChangePassword">
            <div class="form-group">
              <label for="old_password">当前密码</label>
              <input
                type="password"
                id="old_password"
                v-model="passwordForm.old_password"
                class="form-input"
                placeholder="请输入当前密码"
                required
              />
            </div>

            <div class="form-group">
              <label for="new_password">新密码</label>
              <input
                type="password"
                id="new_password"
                v-model="passwordForm.new_password"
                class="form-input"
                placeholder="请输入新密码（至少6位）"
                minlength="6"
                required
              />
            </div>

            <div class="form-group">
              <label for="confirm_password">确认新密码</label>
              <input
                type="password"
                id="confirm_password"
                v-model="passwordForm.confirm_password"
                class="form-input"
                placeholder="请再次输入新密码"
                minlength="6"
                required
              />
            </div>

            <div class="form-actions">
              <button type="button" @click="closePasswordModal" class="btn btn-outline">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
                {{ passwordLoading ? '修改中...' : '确认修改' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  padding: var(--spacing-xl);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing);
  border-bottom: 1px solid var(--border-light);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-buttons {
  display: flex;
  gap: var(--spacing);
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: all var(--transition);
  cursor: pointer;
  border: none;
}

.btn-back {
  background-color: var(--gray-100);
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
}

.btn-back:hover {
  background-color: var(--gray-200);
  color: var(--text-primary);
}

.btn-logout {
  background-color: var(--red-500);
  color: white;
}

.btn-logout:hover {
  background-color: var(--red-600);
}

.btn-primary {
  background-color: var(--primary-500);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-600);
}

.btn-primary:disabled {
  background-color: var(--gray-300);
  cursor: not-allowed;
}

.btn-outline {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
}

.btn-outline:hover {
  background-color: var(--gray-100);
  color: var(--text-primary);
}

.profile-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-2xl);
  max-width: 600px;
  margin: 0 auto;
}

.profile-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.avatar {
  width: 100px;
  height: 100px;
  background-color: var(--primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--spacing);
}

.avatar-text {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
}

.user-name {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm);
}

.user-role {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: var(--primary-100);
  color: var(--primary-700);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: 500;
}

.profile-info {
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  padding: var(--spacing-xl) 0;
  margin-bottom: var(--spacing-xl);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing) 0;
}

.info-item label {
  font-weight: 500;
  color: var(--text-secondary);
}

.info-item span {
  font-weight: 600;
  color: var(--text-primary);
}

.profile-actions {
  text-align: center;
}

/* 模态框样式 */
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
}

.modal-close:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-xl);
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
}

.form-actions {
  display: flex;
  gap: var(--spacing);
  justify-content: flex-end;
  margin-top: var(--spacing-xl);
}

.alert {
  padding: var(--spacing);
  border-radius: var(--radius);
  margin-bottom: var(--spacing);
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
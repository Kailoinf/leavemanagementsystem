<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  importStudents,
  importTeachers,
  importReviewers,
  downloadImportTemplate
} from '../api'

// 导入类型
type ImportType = 'student' | 'teacher' | 'reviewer'

// 当前选中的导入类型
const currentType = ref<ImportType>('student')

// 文件上传相关状态
const isUploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')
const selectedFile = ref<File | null>(null)
const uploadResult = ref<any>(null)

// 默认密码
const defaultPassword = ref('123456')

// 导入类型描述
const typeDescriptions: Record<ImportType, string> = {
  student: '学生（学号,姓名,学院,班级,专业,辅导员ID）',
  teacher: '教师（工号,姓名,部门,职称）',
  reviewer: '审核员（工号,姓名,学院,审核员身份）'
}

// 切换导入类型
const handleTypeChange = (type: ImportType) => {
  currentType.value = type
  selectedFile.value = null
  uploadError.value = ''
  uploadSuccess.value = ''
  uploadResult.value = null
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null

  // 验证文件类型
  if (file && !file.name.endsWith('.csv')) {
    uploadError.value = '请上传 CSV 格式的文件'
    selectedFile.value = null
    return
  }

  selectedFile.value = file
  uploadError.value = ''
  uploadSuccess.value = ''
  uploadResult.value = null
}

// 处理拖拽上传
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()

  const file = event.dataTransfer?.files?.[0] || null

  // 验证文件类型
  if (file && !file.name.endsWith('.csv')) {
    uploadError.value = '请上传 CSV 格式的文件'
    selectedFile.value = null
    return
  }

  selectedFile.value = file
  uploadError.value = ''
  uploadSuccess.value = ''
  uploadResult.value = null
}

// 下载模板
const handleDownloadTemplate = async () => {
  try {
    uploadError.value = ''
    await downloadImportTemplate(currentType.value)
    uploadSuccess.value = '模板下载成功'
    setTimeout(() => {
      uploadSuccess.value = ''
    }, 3000)
  } catch (error: any) {
    console.error('下载模板失败:', error)
    uploadError.value = error.response?.data?.detail || '下载模板失败，请重试'
  }
}

// 执行导入
const handleImport = async () => {
  if (!selectedFile.value) {
    uploadError.value = '请先选择要导入的文件'
    return
  }

  try {
    isUploading.value = true
    uploadError.value = ''
    uploadSuccess.value = ''
    uploadResult.value = null

    let result
    switch (currentType.value) {
      case 'student':
        result = await importStudents(selectedFile.value, defaultPassword.value)
        break
      case 'teacher':
        result = await importTeachers(selectedFile.value, defaultPassword.value)
        break
      case 'reviewer':
        result = await importReviewers(selectedFile.value, defaultPassword.value)
        break
    }

    uploadResult.value = result
    uploadSuccess.value = `导入成功！共导入 ${result.result?.success_count || 0} 条记录`

    // 清空文件选择
    selectedFile.value = null
    const fileInput = document.getElementById('file-input') as HTMLInputElement
    if (fileInput) {
      fileInput.value = ''
    }

  } catch (error: any) {
    console.error('导入失败:', error)
    uploadError.value = error.response?.data?.detail || '导入失败，请重试'
    uploadResult.value = error.response?.data
  } finally {
    isUploading.value = false
  }
}

// 清除上传结果
const clearResult = () => {
  uploadResult.value = null
  uploadSuccess.value = ''
  uploadError.value = ''
}
</script>

<template>
  <div class="data-import-page">
    <div class="import-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">批量导入数据</h1>
        <p class="page-subtitle">支持批量导入学生、教师和审核员数据</p>
      </div>

      <!-- 导入类型选择 -->
      <div class="type-selector">
        <button
          v-for="type in ['student', 'teacher', 'reviewer'] as ImportType[]"
          :key="type"
          @click="handleTypeChange(type)"
          :class="['type-btn', { active: currentType === type }]"
        >
          <span class="type-icon">{{ type === 'student' ? '👨‍🎓' : type === 'teacher' ? '👨‍🏫' : '👨‍💼' }}</span>
          <span class="type-label">{{ type === 'student' ? '学生' : type === 'teacher' ? '教师' : '审核员' }}</span>
        </button>
      </div>

      <!-- 模板下载区域 -->
      <div class="template-section">
        <div class="template-info">
          <div class="info-header">
            <span class="info-icon">📋</span>
            <div class="info-content">
              <h3>导入格式</h3>
              <p>{{ typeDescriptions[currentType] }}</p>
            </div>
          </div>
          <button @click="handleDownloadTemplate" class="btn btn-outline">
            下载模板
          </button>
        </div>
      </div>

      <!-- 文件上传区域 -->
      <div class="upload-section">
        <div
          :class="['upload-area', { 'drag-over': false, 'has-file': selectedFile }]"
          @dragover="handleDragOver"
          @drop="handleDrop"
        >
          <input
            type="file"
            id="file-input"
            accept=".csv"
            @change="handleFileSelect"
            class="file-input"
          />
          <label for="file-input" class="upload-label">
            <div class="upload-icon">
              <span v-if="!selectedFile">📁</span>
              <span v-else>✅</span>
            </div>
            <div class="upload-text">
              <p class="upload-title">
                {{ selectedFile ? selectedFile.name : '点击或拖拽文件到此处' }}
              </p>
              <p class="upload-subtitle">
                {{ selectedFile ? '文件已选择' : '支持 CSV 格式，最大 10MB' }}
              </p>
            </div>
          </label>
        </div>

        <!-- 默认密码设置 -->
        <div class="default-password-section">
          <label for="default-password" class="password-label">
            默认密码
          </label>
          <input
            type="text"
            id="default-password"
            v-model="defaultPassword"
            class="password-input"
            placeholder="默认: 123456"
            maxlength="32"
          />
        </div>

        <!-- 导入按钮 -->
        <button
          @click="handleImport"
          class="btn btn-primary btn-lg"
          :disabled="!selectedFile || isUploading"
        >
          <span v-if="!isUploading">开始导入</span>
          <span v-else>导入中...</span>
        </button>
      </div>

      <!-- 导入结果显示 -->
      <div v-if="uploadResult" class="result-section">
        <div class="result-header">
          <h3>导入结果</h3>
          <button @click="clearResult" class="btn-close">✕</button>
        </div>

        <div v-if="uploadResult.result" class="result-content">
          <div class="result-item success">
            <span class="result-icon">✅</span>
            <div class="result-text">
              <p class="result-label">成功导入</p>
              <p class="result-value">{{ uploadResult.result.success_count || 0 }} 条记录</p>
            </div>
          </div>

          <div v-if="uploadResult.result.failed_count > 0" class="result-item failed">
            <span class="result-icon">❌</span>
            <div class="result-text">
              <p class="result-label">导入失败</p>
              <p class="result-value">{{ uploadResult.result.failed_count }} 条记录</p>
            </div>
          </div>

          <div v-if="uploadResult.result.errors && uploadResult.result.errors.length > 0" class="error-details">
            <h4>错误详情</h4>
            <ul class="error-list">
              <li v-for="(error, index) in uploadResult.result.errors.slice(0, 10)" :key="index" class="error-item">
                {{ error }}
              </li>
              <li v-if="uploadResult.result.errors.length > 10" class="error-item">
                ... 还有 {{ uploadResult.result.errors.length - 10 }} 条错误
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="uploadError" class="alert alert-danger">
        <span class="alert-icon">⚠️</span>
        <span class="alert-text">{{ uploadError }}</span>
      </div>

      <!-- 成功提示 -->
      <div v-if="uploadSuccess && !uploadResult" class="alert alert-success">
        <span class="alert-icon">✅</span>
        <span class="alert-text">{{ uploadSuccess }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.data-import-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--bg-secondary) 100%);
  padding: var(--spacing-xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-container {
  width: 100%;
  max-width: 800px;
  background-color: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-xl);
  border: 1px solid var(--border-light);
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0;
}

/* 导入类型选择 */
.type-selector {
  display: flex;
  gap: var(--spacing);
  margin-bottom: var(--spacing-lg);
  justify-content: center;
}

.type-btn {
  flex: 1;
  max-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing);
  background-color: var(--bg-secondary);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition);
}

.type-btn:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--primary-300);
}

.type-btn.active {
  background-color: var(--primary-50);
  border-color: var(--primary-500);
  color: var(--primary-600);
}

.type-icon {
  font-size: 2rem;
}

.type-label {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

/* 模板下载区域 */
.template-section {
  margin-bottom: var(--spacing-lg);
}

.template-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.info-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.info-icon {
  font-size: 1.5rem;
}

.info-content h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.info-content p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* 文件上传区域 */
.upload-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.upload-area {
  position: relative;
  border: 2px dashed var(--border-medium);
  border-radius: var(--radius-lg);
  background-color: var(--bg-secondary);
  transition: all var(--transition);
  overflow: hidden;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: var(--primary-500);
  background-color: var(--primary-50);
}

.upload-area.has-file {
  border-color: var(--success-500);
  background-color: var(--success-50);
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl) var(--spacing);
  cursor: pointer;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
  transition: transform var(--transition);
}

.upload-area:hover .upload-icon {
  transform: scale(1.1);
}

.upload-text {
  text-align: center;
}

.upload-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.upload-subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* 默认密码设置 */
.default-password-section {
  display: flex;
  align-items: center;
  gap: var(--spacing);
  padding: var(--spacing-md);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.password-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  min-width: 80px;
}

.password-input {
  flex: 1;
  padding: 0.625rem 0.875rem;
  font-size: var(--text-base);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all var(--transition);
}

.password-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* 导入结果显示 */
.result-section {
  padding: var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.result-header h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius);
  transition: all var(--transition);
}

.btn-close:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
}

.result-item.success {
  background-color: var(--success-50);
  border: 1px solid var(--success-200);
}

.result-item.failed {
  background-color: var(--error-50);
  border: 1px solid var(--error-200);
}

.result-icon {
  font-size: 1.5rem;
}

.result-text {
  flex: 1;
}

.result-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--spacing-xs) 0;
}

.result-value {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.error-details {
  margin-top: var(--spacing-md);
}

.error-details h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.error-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.error-item {
  font-size: var(--text-sm);
  color: var(--error-600);
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--error-50);
  border-radius: var(--radius);
  margin-bottom: var(--spacing-xs);
}

/* 警告提示 */
.alert {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  margin-top: var(--spacing-md);
}

.alert-danger {
  background-color: var(--error-50);
  border: 1px solid var(--error-200);
  color: var(--error-600);
}

.alert-success {
  background-color: var(--success-50);
  border: 1px solid var(--success-200);
  color: var(--success-600);
}

.alert-icon {
  font-size: 1.25rem;
}

.alert-text {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-import-page {
    padding: var(--spacing-md);
  }

  .import-container {
    padding: var(--spacing-lg);
  }

  .type-selector {
    flex-direction: column;
  }

  .type-btn {
    max-width: 100%;
    flex-direction: row;
    justify-content: center;
  }
}
</style>

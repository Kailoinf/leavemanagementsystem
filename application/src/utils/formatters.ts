/* 通用格式化工具函数 */

/**
 * 格式化日期显示
 * @param dateString 日期字符串
 * @returns 格式化后的日期字符串
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const currentYear = new Date().getFullYear()
  const dateYear = date.getFullYear()

  if (dateYear === currentYear) {
    // 本年，只显示月日
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}-${day}`
  } else {
    // 非本年，显示年月日
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${year}-${month}-${day}`
  }
}

/**
 * 根据状态获取徽章样式类
 * @param status 状态字符串
 * @returns 对应的CSS类名
 */
export const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case '已批准':
      return 'badge-success'
    case '待审批':
      return 'badge-warning'
    case '已拒绝':
      return 'badge-danger'
    case '已撤销':
      return 'badge-secondary'
    default:
      return 'badge-primary'
  }
}
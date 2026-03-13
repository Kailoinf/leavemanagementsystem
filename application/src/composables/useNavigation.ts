/* 导航相关组合式函数 */

import { useRouter } from 'vue-router'

/**
 * 页面导航组合式函数
 * @returns 包含导航方法的对象
 */
export function useNavigation() {
  const router = useRouter()

  /**
   * 返回首页
   */
  const goToHome = () => {
    router.push('/')
  }

  /**
   * 跳转到学生列表
   */
  const goToStudents = () => {
    router.push('/students')
  }

  /**
   * 跳转到请假条列表
   */
  const goToLeaves = () => {
    router.push('/leaves')
  }

  /**
   * 跳转到审核员列表
   */
  const goToReviewers = () => {
    router.push('/reviewers')
  }

  /**
   * 跳转到教师列表
   */
  const goToTeachers = () => {
    router.push('/teachers')
  }

  /**
   * 跳转到课程列表
   */
  const goToCourses = () => {
    router.push('/courses')
  }

  /**
   * 返回上一页
   */
  const goBack = () => {
    router.back()
  }

  return {
    goToHome,
    goToStudents,
    goToLeaves,
    goToReviewers,
    goToTeachers,
    goToCourses,
    goBack
  }
}
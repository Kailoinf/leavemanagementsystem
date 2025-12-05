#import "@preview/gakusyun-doc:1.0.0": *

// 设置模板参数
#show: docu.with(
  title: "Leave Management System",
  subtitle: "工作日志",
  author: "X. J. Gao",
  show-title: true,
  title-page: false,
  blank-page: true,
  show-index: true,
  index-page: false,
  column-of-index: 1,
  depth-of-index: 3,
  cjk-font: "Source Han Serif",
  emph-cjk-font: "FandolKai",
  latin-font: "New Computer Modern",
  mono-font: "Maple Mono NF",
  default-size: "小四",
  lang: "zh",
  region: "cn",
  paper: "a4",
  // margin: (left: 3.18cm, right: 3.18cm, top: 2.54cm, bottom: 2.54cm),
  margin: 1.5cm,
  date: datetime.today().display("[year]年[month]月[day]日"),
  numbering: "第1页 共1页",
  column: 2,
)
= 2025年12月4日
== 目前已完成
+ 后端
  - 数据库的创建
  - 数据库查询包括表行数、查询表、通过id查询行的GET方法
  - 创建学生、审核员、教师、课程表、请假表的POST方法
  - 通过用户（学生、审核员、教师、课程）id查询请假的记录的方法
  - 最基本的登录、验证
+ 网页前端
  - 首页显示所有的数据
  - 点击进入分页列表显示
+ 小程序端
  - 前端所有功能
  - 扫码的按钮（无任何处理逻辑）

== TODO
+ 后端

+ 网页前端
  - 创建请假条的实现
  - 登录，分角色显示内容
+ 小程序端
  - 扫码功能的完善，可以通过扫码登录网页前端
== 已知问题·
担保权限不是在期限内有权限，而是这个时间以后的才有权限。

如果违规，惩罚就是把担保权限时间移到today+7、30、90、180天不等

= 未来设想
- 扫码考勤

= 2025年12月5日
== 目前已完成
+ 后端
  - 登录及验证
+ 前端
  - 登录及验证
+ 小程序端
  - 小程序端扫码登录前端



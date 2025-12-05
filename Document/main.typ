#import "@preview/gakusyun-doc:1.0.0": *

// 设置模板参数
#show: docu.with(
  title: "Leave Management System",
  subtitle: "技术实现及部署文档",
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
  margin: 1.2cm,
  date: datetime.today().display("[year]年[month]月[day]日"),
  numbering: "第1页 共1页",
  column: 2,
)

#show table: set align(center)
#show table: set text(size: zh("小五"))

使用0*古法编程*，$99. dot(9)%$使用生成式人工智能。

此文档不含任何生成式Ai内容。

= LMS
LMS请假管理系统是《基于微信小程序的高校学生请假管理系统的设计与实现》的代码实现。

本项目是一个基于微信小程序 + Fastapi 后端的智能请假管理系统，包含学生、审核员、教师、管理员等多个角色。前端采用微信小程序 Vue mini 框架实现，网页版前端使用 Vue 实现，后端使用 Python + Fastapi 实现 RESTful API 接口，数据库使用 SQLite 并通过 ORM 进行操作。

== 用户角色与权限

- 学生
  - 提交请假申请（一般/长假/紧急）
  - 查看审批状态与历史记录
  - 可被担保（紧急情况）
  - 导出个人请假记录

- 审核员
  - 审批请假申请（按权限分级）
  - 批量处理请假条
  - 直接创建请假条
  - 留言要求补充材料
  - 导出数据

- 教师
  - 查看课程请假情况
  - 统计缺勤率
  - 导出 CSV / Excel / JSON
  - 生成图表

- 管理员
  - 用户管理（增删改查）
  - 权限设置
  - 日志查看
  - 数据备份
  - 批量导入用户
  - 批量创建请假条

== 鉴权机制

1. 审核通过后，服务器用私钥加密生成二维码。
2. 鉴权端扫码获取密文与明文。
3. 使用公钥解密并与明文比对。
4. 若一致，则从后端获取完整请假信息并判断是否在合法时间内。

== 审核权限等级

- *1天以内*：辅导员批准
- *2\~3天*：院党总支副书记批准
- *4\~7天*：院党总支书记批准
- *7天以上*：学生工作处批准

== 数据库设计
=== student - 学生用户表
#table(
  columns: 4,
  stroke: none,
  table.hline(),
  table.header([列名], [类型], [是否为空], [说明]),
  table.hline(stroke: 0.5pt),
  [学号], [char(12)], [NO], [主键],
  [姓名], [char(8)], [NO], [-],
  [密码], [CHAR(32)], [YES], [MD5 加密],
  [学院], [char(8)], [YES], [用于权限控制],
  [辅导员], [char(12)], [YES], [外键],
  [担保权限], [Datetime], [NO], [默认为0，表示可担保时间],
  table.hline(),
)

=== reviewer - 审核员表
#table(
  columns: 4,
  stroke: none,
  table.hline(),
  table.header([列名], [类型], [是否为空], [说明]),
  table.hline(stroke: 0.5pt),
  [工号], [char(12)], [NO], [主键],
  [姓名], [char(8)], [NO], [-],
  [学院], [char(8)], [YES], [控制权限范围],
  [审核员身份], [varchar(10)], [YES], [导员、书记、学工处],
  [密码], [CHAR(32)], [YES], [MD5 加密],
  table.hline(),
)

=== teacher - 教师表
#table(
  columns: 4,
  stroke: none,
  table.hline(),
  table.header([列名], [类型], [是否为空], [说明]),
  table.hline(stroke: 0.5pt),
  [工号], [char(12)], [NO], [主键],
  [姓名], [char(8)], [NO], [-],
  [密码], [CHAR(32)], [YES], [MD5 加密],
  table.hline(),
)

=== leave - 请假记录表
#table(
  columns: 4,
  stroke: none,
  table.hline(),
  table.header([列名], [类型], [是否为空], [说明]),
  table.hline(stroke: 0.5pt),
  [请假编号], [char(12)], [NO], [主键],
  [请假学生ID], [char(12)], [NO], [外键],
  [请假日期], [Datetime], [NO], [-],
  [课时数], [char(8)], [YES], [-],
  [请假天数], [char(8)], [NO], [-],
  [状态], [char(8)], [NO], [审核中、已通过、已拒绝、无效],
  [请假类型], [Char(8)], [YES], [病假、事假、公假],
  [请假备注], [char(100)], [YES], [学生填写],
  [材料], [Char(100)], [YES], [材料链接],
  [审核员], [char(12)], [YES], [外键],
  [教师], [char(12)], [YES], [外键],
  [审核备注], [char(100)], [YES], [审核留言],
  [审核时间], [Datetime], [YES], [-],
  [课程id], [Char(12)], [YES], [外键],
  [是否修改], [Char(12)], [YES], [修改后指向新请假编号],
  [担保学生id], [char(12)], [YES], [外键],
  table.hline(),
)

=== course - 课程表
#table(
  columns: 4,
  stroke: none,
  table.hline(),
  table.header([列名], [类型], [是否为空], [说明]),
  table.hline(stroke: 0.5pt),
  [课程id], [char(12)], [NO], [主键],
  [授课教师], [char(12)], [NO], [外键],
  [课程名], [CHAR(12)], [NO], [-],
  [课时数], [Char(8)], [YES], [-],
  table.hline(),
)

= Backend
- 用户权限管理
  - 登录鉴权（JWT）
  - 角色权限验证
  - 使用拦截器防止未登录访问

- 数据接口
  - RESTful API 设计
  - ORM 操作数据库（防止 SQL 注入）
  - 对象存储上传下载材料

- 系统设置
  - 日志记录
  - 数据备份
  - 用户批量导入（CSV/XLSX）
== 部署

1. 本项目使用UV作为包管理器，在部署时使用`uv sync`命令即可自动安装依赖。
2. 创建配置文件，`config_sample.toml`为模板，复制为`config.toml`。
3. 完成上述步骤后，便可使用`uvicorn`进行部署。完整操作如@deployBackend 所示。
#figure(
  ```bash
  uv sync

  cp config_sample.toml config.toml

  uvicorn main:app --reload
  ```,
  caption: "部署后端",
)<deployBackend>

= Frontend

- 首页
  - 创建请假条（学生/审核员）
  - 显示最近请假条（按状态颜色区分）
  - 审核员可进入待审核列表
  - 长时间未处理的请假条置顶

- 我的页面
  - 显示个人信息
  - 历史请假条（学生）
  - 所带课程请假统计（教师）
  - 所带学生请假汇总（辅导员）
  - 学院所有请假（书记）
  - 全校请假（学工处）
  - 支持导出功能

== 部署
1. 使用`npm install`安装依赖项
2. 使用`npm run build`编译代码，把`dist`目录下的文件复制到如Nginx、Caddy等网页服务器下。
3. 配置服务器。
= Mini Program

- 首页：创建请假条、显示请假条列表
  - 请假详情：编辑、查看详情、提交材料
- 我的：个人信息、历史记录、导出功能
- 鉴权页：扫码验证请假有效性
- 扫码登录网页、PC端
  - 如何实现：生成二维码时生成一个token，通过扫码传到手机上。用手机已验证的账号Post到服务器注册。
  - 手机端登录也如此，用手机生成token，然后和账号密码一起传到服务器注册。

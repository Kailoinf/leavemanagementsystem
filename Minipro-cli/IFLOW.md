# 请假管理系统 (Minipro-cli)

## 项目概述

这是一个基于 Vue Mini 框架开发的微信小程序请假管理系统。该系统为教育机构提供完整的请假管理功能，支持学生、教师、审核员等多种角色，实现请假申请、审批、数据统计等核心业务流程。

### 技术栈

- **前端框架**: Vue Mini (基于 Vue 3 的微信小程序开发框架)
- **编程语言**: TypeScript
- **构建工具**: Rollup + Babel
- **样式处理**: PostCSS
- **UI 组件**: 自定义组件，支持暗色模式
- **API 通信**: 微信小程序 wx.request API

### 项目架构

```
src/
├── app.ts              # 应用入口文件，配置 API 基础 URL
├── app.json            # 小程序配置文件，定义页面路由和导航栏
├── app.css             # 全局样式文件
├── theme.json          # 主题配置文件，支持暗色模式
├── sitemap.json        # 站点地图配置
├── pages/              # 页面目录
│   ├── login/          # 登录页面
│   ├── home/           # 首页，显示系统统计数据
│   ├── mine/           # 个人中心页面
│   ├── students/       # 学生管理页面
│   ├── leaves/         # 请假条管理页面
│   ├── reviewers/      # 审核员管理页面
│   ├── teachers/       # 教师管理页面
│   └── courses/        # 课程管理页面
├── images/             # 图片资源目录
└── utils/              # 工具函数目录
    └── auth.ts         # 认证相关工具函数
```

## 构建和运行

### 环境要求

- Node.js >= 18.19.1 < 19 || >= 20.6.1
- 微信开发者工具

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

开发模式会启动文件监听，实时编译源代码到 `dist` 目录，并在微信开发者工具中实时预览。

### 生产构建

```bash
npm run build
```

生产构建会进行代码压缩和优化，输出到 `dist` 目录。

### 类型检查

```bash
npm run type-check
```

运行 TypeScript 类型检查，确保代码类型安全。

## 微信开发者工具配置

1. 打开微信开发者工具
2. 选择 **导入项目**
3. 项目目录选择当前项目根目录（`C:\Users\gaoxj\Projects\LMS\Minipro-cli`）
4. **重要**: 不要选择 `dist` 目录作为项目根目录
5. AppID 使用项目配置文件中的 `wx065763e35362a1bc`

## API 配置

项目支持多环境 API 配置，在 `src/app.ts` 中修改 `BASE_URL`:

```typescript
// 开发环境
export const BASE_URL = 'http://localhost:8000/api/v1';

// 生产环境
// export const BASE_URL = 'https://amazon.gxj62.cn/api/v1';
```

## 核心功能

### 认证系统

- **登录功能**: 支持账号密码登录 (`src/pages/login/index.ts`)
- **Token 管理**: 自动生成和管理用户 token
- **权限检查**: 基于角色的访问控制 (`src/utils/auth.ts`)
- **扫码登录**: 支持二维码快速登录

### 数据管理

- **首页统计**: 显示学生、教师、课程、请假条和审核员数量 (`src/pages/home/index.ts`)
- **CRUD 操作**: 各模块支持完整的增删改查功能
- **数据同步**: 实时从后端 API 获取最新数据

### 用户界面

- **响应式设计**: 适配不同屏幕尺寸
- **暗色模式**: 支持系统暗色模式自动切换
- **导航结构**: 底部 Tab 导航，页面间流畅跳转

## 开发约定

### 代码风格

- 使用 TypeScript 进行类型安全开发
- 遵循 Vue 3 Composition API 编程范式
- 使用 `defineComponent` 定义页面组件
- 统一使用 `ref` 和 `reactive` 管理响应式状态

### 文件命名

- 页面文件使用小写字母和连字符: `page-name/index.ts`
- 组件文件使用 PascalCase: `ComponentName.ts`
- 工具函数文件使用小写字母和连字符: `auth.ts`

### API 调用规范

- 统一使用 `wx.request` 进行 API 调用
- API 基础 URL 从 `src/app.ts` 导入
- 请求成功后进行数据类型检查和错误处理
- 统一的错误提示和加载状态管理

### 构建流程

项目使用自定义构建脚本 `build.js`，支持:

- TypeScript/JavaScript 编译
- HTML 转 WXML
- CSS 转 WXSS
- 依赖打包和优化
- 开发模式热更新
- 生产模式代码压缩

## 部署注意事项

1. **环境切换**: 部署前确保修改 `src/app.ts` 中的 `BASE_URL` 为生产环境地址
2. **构建检查**: 运行 `npm run build` 确保构建无错误
3. **类型检查**: 运行 `npm run type-check` 确保无类型错误
4. **微信开发者工具**: 确保项目设置正确，特别是项目根目录配置

## 常见问题

### Q: 微信开发者工具中预览空白?
A: 确保项目根目录设置正确，应该选择项目根目录而非 `dist` 目录。

### Q: API 请求失败?
A: 检查 `src/app.ts` 中的 `BASE_URL` 配置是否正确，以及后端服务是否正常运行。

### Q: 构建失败?
A: 确保安装了所有依赖 `npm install`，并检查 Node.js 版本是否符合要求。
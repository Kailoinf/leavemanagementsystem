# Leave Management System

请假管理系统

## 📖 项目简介

一个简单高效的请假管理系统，用于管理学生/员工的请假申请、审批流程。

## 🏗️ 技术栈

### 后端
- Python 3.14+
- FastAPI
- SQLModel
- Uvicorn
- uv (包管理器)

### 前端
- Vue 3
- TypeScript
- Vite
- Axios
- Vue Router

## 🚀 快速开始

### 后端

```bash
cd Backend

# 安装依赖
uv sync

# 运行
uv run python main.py
```

后端服务将在 `http://localhost:8000` 启动

API 文档：`http://localhost:8000/docs`

### 前端

```bash
cd Frontend

# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建
pnpm build
```

前端服务将在 `http://localhost:5173` 启动

## 📁 项目结构

```
leavemanagementsystem/
├── Backend/               # 后端代码
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── database/     # 数据库配置
│   │   └── models/       # 数据模型
│   └── main.py           # 应用入口
├── Frontend/              # 前端代码
│   └── src/
│       ├── components/   # 组件
│       ├── views/        # 页面
│       └── router/       # 路由配置
└── Document/              # 项目文档
```

## 📄 License

MIT

---

**Made with ❤️ by Kailoinf**

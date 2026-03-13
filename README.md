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

### 一键安装和启动（推荐）

```bash
# 安装所有依赖（前端 + 后端）
make install

# 启动前后端开发服务器
make dev

# 运行所有测试
make test-all
```

### 使用 Makefile

```bash
# 查看所有可用命令
make help
```

### 后端

```bash
cd Backend

# 安装依赖
uv sync

# 安装开发依赖（测试）
pip install -r requirements-dev.txt

# 运行
uv run python main.py
```

后端服务将在 `http://localhost:8000` 启动

API 文档：`http://localhost:8000/docs`

**运行测试**：
```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_auth.py
```

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

**运行测试**：
```bash
# 运行所有测试
pnpm test

# 运行测试并查看覆盖率
pnpm test:coverage

# 打开测试 UI 界面
pnpm test:ui
```

## 📁 项目结构

```
leavemanagementsystem/
├── Backend/               # 后端代码
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── database/     # 数据库配置
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── tests/            # 后端测试
│   │   ├── conftest.py   # pytest 配置
│   │   ├── test_auth.py  # 认证测试
│   │   └── test_api.py   # API 测试
│   └── main.py           # 应用入口
├── Frontend/              # 前端代码
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── views/        # 页面
│   │   ├── router/       # 路由配置
│   │   ├── utils/        # 工具函数
│   │   └── tests/        # 前端测试
│   │       ├── setup.ts  # vitest 配置
│   │       ├── http.test.ts
│   │       └── storage.test.ts
│   └── vitest.config.ts  # 测试配置
└── Document/              # 项目文档
```

## 📄 License

MIT

---

**Made with ❤️ by Kailoinf**

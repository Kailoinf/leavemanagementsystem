.PHONY: help install-backend install-frontend test-backend test-frontend test-all clean lint

# 默认目标
help:
	@echo "Leave Management System - 自动化任务"
	@echo ""
	@echo "可用命令:"
	@echo "  make install-backend    - 安装后端依赖"
	@echo "  make install-frontend    - 安装前端依赖"
	@echo "  make install            - 安装所有依赖"
	@echo "  make test-backend       - 运行后端测试"
	@echo "  make test-frontend      - 运行前端测试"
	@echo "  make test-all           - 运行所有测试"
	@echo "  make dev-backend        - 启动后端开发服务器"
	@echo "  make dev-frontend       - 启动前端开发服务器"
	@echo "  make dev                - 启动前后端开发服务器"
	@echo "  make clean              - 清理临时文件"
	@echo "  make build-frontend     - 构建前端"
	@echo "  make lint-backend       - 后端代码检查"

# 安装后端依赖
install-backend:
	@echo "📦 安装后端依赖..."
	cd Backend && uv sync --extra dev

# 安装前端依赖
install-frontend:
	@echo "📦 安装前端依赖..."
	cd Frontend && pnpm install

# 安装所有依赖
install: install-backend install-frontend
	@echo "✅ 所有依赖安装完成"

# 运行后端测试
test-backend:
	@echo "🧪 运行后端测试..."
	cd Backend && pytest -v --cov=app --cov-report=term-missing

# 运行前端测试
test-frontend:
	@echo "🧪 运行前端测试..."
	cd Frontend && pnpm test

# 运行所有测试
test-all: test-backend test-frontend
	@echo "✅ 所有测试完成"

# 启动后端开发服务器
dev-backend:
	@echo "🚀 启动后端开发服务器..."
	cd Backend && uv run python main.py

# 启动前端开发服务器
dev-frontend:
	@echo "🚀 启动前端开发服务器..."
	cd Frontend && pnpm dev

# 启动前后端开发服务器
dev:
	@echo "🚀 启动前后端开发服务器..."
	@make -j2 dev-backend dev-frontend

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -prune -o -type d -name ".vite" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.db" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

# 构建前端
build-frontend:
	@echo "🔨 构建前端..."
	cd Frontend && pnpm build
	@echo "✅ 前端构建完成"

# 后端代码检查
lint-backend:
	@echo "🔍 后端代码检查..."
	cd Backend && python -m py_compile app/*.py app/*/*.py
	@echo "✅ 代码检查通过"

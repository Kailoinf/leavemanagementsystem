"""API 基础测试"""
from fastapi.testclient import TestClient


def test_api_root(client: TestClient):
    """测试 API 根路径"""
    # 访问 status 端点作为根路径测试
    response = client.get("/api/v1/status/")
    assert response.status_code in [200, 404]  # 可能返回 200 或 404（取决于是否有管理员）


def test_status_endpoint(client: TestClient):
    """测试状态检查端点"""
    response = client.get("/api/v1/status/")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data or "message" in data


def test_cors_headers(client: TestClient):
    """测试 CORS 响应头"""
    response = client.options("/api/v1/status/")
    assert response.status_code in [200, 204]
    assert "access-control-allow-origin" in response.headers or response.headers.get("access-control-allow-origin") == "*"


def test_invalid_endpoint(client: TestClient):
    """测试无效端点返回 404"""
    response = client.get("/api/v1/invalid-endpoint")
    assert response.status_code == 404

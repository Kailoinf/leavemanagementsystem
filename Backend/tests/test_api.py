"""API 基础测试"""
from fastapi.testclient import TestClient


def test_api_root(client: TestClient):
    """测试 API 根路径"""
    response = client.get("/")
    assert response.status_code == 200


def test_status_endpoint(client: TestClient):
    """测试状态检查端点"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "message" in data


def test_cors_headers(client: TestClient):
    """测试 CORS 响应头"""
    response = client.options("/")
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_invalid_endpoint(client: TestClient):
    """测试无效端点返回 404"""
    response = client.get("/api/v1/invalid-endpoint")
    assert response.status_code == 404

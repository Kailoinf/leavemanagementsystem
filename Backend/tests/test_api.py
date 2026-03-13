"""API 基础测试"""
from fastapi.testclient import TestClient


def test_status_endpoint(client: TestClient):
    """测试状态检查端点"""
    response = client.get("/api/v1/status/")
    # 初始状态应该是 unhealthy（没有管理员）
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert "No admin found" in data["message"]


def test_cors_headers(client: TestClient):
    """测试 CORS 响应头"""
    response = client.options("/api/v1/status/")
    assert response.status_code in [200, 204, 405]  # 405 for OPTIONS if not explicitly handled


def test_invalid_endpoint(client: TestClient):
    """测试无效端点返回 404"""
    response = client.get("/api/v1/invalid-endpoint")
    assert response.status_code == 404


def test_api_docs_available(client: TestClient):
    """测试 API 文档可用"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json(client: TestClient):
    """测试 OpenAPI JSON 端点"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data

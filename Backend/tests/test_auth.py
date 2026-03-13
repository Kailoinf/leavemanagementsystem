"""认证相关测试"""
from fastapi.testclient import TestClient


def test_login_check_without_token(client: TestClient):
    """测试无 token 检查登录状态"""
    response = client.get("/api/v1/auth/login/check")
    assert response.status_code == 401 or "detail" in response.json()


def test_login_check_with_invalid_token(client: TestClient):
    """测试无效 token 检查登录状态"""
    response = client.get("/api/v1/auth/login/check?token=invalid_token")
    assert response.status_code == 401 or "detail" in response.json()


def test_create_admin_when_exists(client: TestClient):
    """测试当已存在管理员时创建管理员"""
    response = client.post(
        "/api/v1/auth/create/admin",
        json={
            "username": "admin2",
            "password": "password123",
            "name": "测试管理员"
        }
    )
    assert response.status_code == 400
    assert "Admin already exists" in response.json()["detail"]


def test_login_with_invalid_credentials(client: TestClient):
    """测试使用错误凭证登录"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401 or response.status_code == 404

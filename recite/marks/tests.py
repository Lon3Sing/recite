from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserAuthTests(APITestCase):
    
    def setUp(self):
        """
        在每个测试方法执行前，设置一个用户（模拟注册）。
        """
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'testuser@example.com'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.register_url = reverse('register')  # 注册接口的 URL
        self.login_url = reverse('token_obtain_pair')  # 登录（获取 JWT Token）的 URL
    
    def test_register_user(self):
        """
        测试用户注册
        """
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(self.register_url, data, format='json')
        # 检查 HTTP 状态码是否为 201（表示已创建）
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 检查响应中是否有 'id' 属性（说明用户已创建）
        self.assertIn('id', response.data)
    
    def test_login_user(self):
        """
        测试用户登录（即获取 JWT Token）
        """
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, data, format='json')
        # 检查 HTTP 状态码是否为 200（表示成功）
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 检查响应中是否有 access 和 refresh token
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_user(self):
        """
        测试无效用户登录（错误的用户名或密码）
        """
        data = {
            'username': 'invaliduser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data, format='json')
        # 检查 HTTP 状态码是否为 401（未授权）
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


from rest_framework import viewsets, permissions, generics, status
from .models import Mark, UserMark
from .serializers import MarkSerializer, UserMarkSerializer, UserRegistrationSerializer, UserUpdateSerializer, ChangePasswordSerializer

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate

# Mark 视图
class MarkViewSet(viewsets.ReadOnlyModelViewSet):  # 只读接口
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [permissions.AllowAny]  # 所有人可访问

    def list(self, request):
        """
        GET /marks/
        列出所有条目，支持按 category 参数筛选。
        """
        category = request.query_params.get('category', None)  # 获取 category 参数
        if category:
            marks = Mark.objects.filter(category=category)
        else:
            marks = Mark.objects.all()

        serializer = MarkSerializer(marks, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        POST /marks/
        创建新条目
        """
        title = request.data.get('title')
        content = request.data.get('content')
        category = request.data.get('category')
        print(content)
        # 参数验证
        if not all([title, content, category]):
            return Response(
                {"detail": "Missing required fields: title, content, or category"},
                status=status.HTTP_400_BAD_REQUEST
            )
        mark = Mark.objects.create(
            title=title,
            content=content,
            category=category
        )
        serializer = MarkSerializer(mark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        GET /marks/{id}/
        查看某个条目的详细信息（通过 id）
        """
        try:
            mark = Mark.objects.get(pk=pk)  # 获取指定 id 的条目
        except Mark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)  # 如果找不到，返回 404

        serializer = MarkSerializer(mark)  # 使用序列化器将数据返回
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        PUT /marks/{id}/
        更新某个条目的信息（全量更新）
        """
        try:
            mark = Mark.objects.get(pk=pk)  # 获取指定 id 的条目
        except Mark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)  # 如果找不到，返回 404

        serializer = MarkSerializer(mark, data=request.data)  # 用新数据进行序列化
        if serializer.is_valid():
            serializer.save()  # 保存更新
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 如果数据无效，返回错误信息

    def partial_update(self, request, pk=None):
        """
        PATCH /marks/{id}/
        更新某个条目的部分信息（部分更新）
        """
        try:
            mark = Mark.objects.get(pk=pk)  # 获取指定 id 的条目
        except Mark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)  # 如果找不到，返回 404

        serializer = MarkSerializer(mark, data=request.data, partial=True)  # 部分更新
        if serializer.is_valid():
            serializer.save()  # 保存更新
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 如果数据无效，返回错误信息

    def destroy(self, request, pk=None):
        """
        DELETE /marks/{id}/
        删除某个条目
        """
        try:
            mark = Mark.objects.get(pk=pk)  # 获取指定 id 的条目
        except Mark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)  # 如果找不到，返回 404

        mark.delete()  # 删除条目
        return Response(status=status.HTTP_204_NO_CONTENT)  # 返回 204 表示删除成功，且没有返回内容

# 用户收藏视图
class UserMarkViewSet(viewsets.ModelViewSet):
    serializer_class = UserMarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 返回当前用户的收藏条目
        return UserMark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 自动关联到当前用户
        serializer.save(user=self.request.user)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserRegistrationSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # 认证用户才能访问

    def get(self, request):
        user = request.user  # 获取当前认证的用户
        user_data = {
            'username': user.username,
            'email': user.email,
        }
        return Response(user_data)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # partial=True 允许部分更新
        if serializer.is_valid():
            serializer.save()  # 保存更新
            return Response(serializer.data)  # 返回更新后的数据
        return Response(serializer.errors, status=400)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            
            # 验证当前密码是否正确
            user = authenticate(username=user.username, password=current_password)
            if user is None:
                return Response({"detail": "Current password is incorrect."}, status=400)
            
            # 更新密码
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully."})
        
        return Response(serializer.errors, status=400)
    

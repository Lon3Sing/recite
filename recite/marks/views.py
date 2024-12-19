from rest_framework import viewsets, permissions, generics, status
from .models import Mark, UserMark
from .serializers import MarkSerializer, UserMarkSerializer, UserRegistrationSerializer, UserUpdateSerializer, ChangePasswordSerializer

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from django.contrib.auth import authenticate
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MarkFilter
from django.db.models import Q

class MarkCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        获取带有用户收藏状态的 Mark 列表，并根据过滤条件进行筛选。
        """
        VALID_SORT_FIELDS = ['id', 'title', 'category', 'created_at']
        
        # 获取当前登录用户
        user = request.user

        # 分页信息
        page = int(request.GET.get('page', 1) if request.GET.get('page', 1) != '' else 1)
        page_size = int(request.GET.get('page_size', 20) if request.GET.get('page_size', 20) != '' else 20)

        # 获取筛选条件
        title = request.GET.get('title', None)
        category = request.GET.get('category', None)
        content = request.GET.get('content', None)
        created_at_after = request.GET.get('created_at_after', None)
        created_at_before = request.GET.get('created_at_before', None)
        search = request.GET.get('search', None)  # 新增 search 参数
        sort_by = request.GET.get('sort_by', None)  # 排序字段
        order = request.GET.get('order', 'desc')  # 排序方式，默认为降序
        
        
        # 验证 sort_by 是否是有效字段
        if sort_by not in VALID_SORT_FIELDS:
            sort_by = 'created_at'

        # 获取查询集
        queryset = Mark.objects.all()

        # 根据 search 参数进行模糊匹配
        if search:
            # 使用 Q 对象进行 OR 查询
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # 根据筛选条件进行过滤
        if title:
            queryset = queryset.filter(title__icontains=title)  # 模糊匹配
        if category:
            queryset = queryset.filter(category__iexact=category)  # 精确匹配
        if content:
            queryset = queryset.filter(content__icontains=content)  # 模糊匹配
        if created_at_after:
            queryset = queryset.filter(created_at__gte=created_at_after)  # 过滤大于等于
        if created_at_before:
            queryset = queryset.filter(created_at__lte=created_at_before)  # 过滤小于等于

        if sort_by:
            if order == 'desc':
                queryset = queryset.order_by(f'-{sort_by}')  # 降序
            else:
                queryset = queryset.order_by(sort_by)  # 升序

        # 获取用户收藏的 Mark ID 列表
        user_marks = UserMark.objects.filter(user=user)
        user_mark_ids = UserMark.objects.filter(user=user).values_list('mark_id', flat=True)
        user_mark_dict = {um.mark_id: um.id for um in user_marks}  # {mark_id: user_mark_id}

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_queryset = queryset[start:end]

        # 将每个 Mark 的数据序列化并添加收藏状态
        marks = []
        for mark in paginated_queryset:
            mark_data = MarkSerializer(mark).data
            mark_data['is_collected'] = mark.id in user_mark_ids  # 判断用户是否收藏
            mark_data['collected_mark_id'] = user_mark_dict.get(mark.id, None)  # 如果收藏了该条目，返回对应收藏记录的 ID
            marks.append(mark_data)

        # 返回分页结果
        total_count = queryset.count()  # 获取所有符合条件的总数
        total_pages = (total_count + page_size - 1) // page_size  # 总页数，向上取整

        # 构建分页信息
        response_data = {
            'count': total_count,
            'total_pages': total_pages,
            'results': marks
        }

        return Response(response_data)

# Mark 视图
class MarkViewSet(viewsets.ReadOnlyModelViewSet):  # 只读接口
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [permissions.AllowAny]  # 所有人可访问
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = MarkFilter  # 引用自定义的过滤器
    search_fields = ['title', 'content', 'category']  # 设置搜索字段，可以选择根据 title, content, category 搜索
    pagination_class = None  # 禁用分页
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 如果你想增加其他的自定义查询条件，可以在这里进一步过滤
        return queryset

    # def list(self, request):
    #     """
    #     GET /marks/
    #     列出所有条目，支持按 category 参数筛选。
    #     """
    #     category = request.query_params.get('category', None)  # 获取 category 参数
    #     if category:
    #         marks = Mark.objects.filter(category=category)
    #     else:
    #         marks = Mark.objects.all()

    #     serializer = MarkSerializer(marks, many=True)
    #     return Response(serializer.data)

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
    
class UserMarkViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        查看用户收藏的条目，支持按时间排序、按类别筛选、分页和搜索
        """
        user = request.user

        category = request.GET.get('category', None)
        sort_by = request.GET.get('sort_by', 'created_at')
        search = request.GET.get('search', None)
        order = request.GET.get('order', 'desc')  # 排序方式，默认为降序

        if order != 'asc' and order != 'desc':
            order = 'desc'
        

        # 定义有效的排序字段
        valid_sort_by_fields = ['created_at', 'id', 'mark', 'preference_level']
        
        # 如果 order_by 无效，默认为 'created_at'
        if sort_by not in valid_sort_by_fields:
            sort_by = 'created_at'

        # 获取分页参数，默认为第1页，每页20条
        page = int(request.GET.get('page', 1) if request.GET.get('page', 1) != '' else 1)
        page_size = int(request.GET.get('page_size', 20) if request.GET.get('page_size', 20) != '' else 20)

        # 查询 UserMark，并根据用户和分类进行筛选
        queryset = UserMark.objects.filter(user=user)
        
        # 根据 category 进行过滤（如果提供）
        if category:
            queryset = queryset.filter(mark__category=category)

        # 如果提供了 search 参数，进行模糊匹配（title 或 content）
        if search:
            queryset = queryset.filter(
                Q(mark__title__icontains=search) | Q(mark__content__icontains=search) | Q(note__icontains=search)
            )
        
        # 根据 order_by 排序
        if sort_by:
            if order == 'desc':
                queryset = queryset.order_by(f'-{sort_by}')  # 降序
            else:
                queryset = queryset.order_by(sort_by)  # 升序

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_queryset = queryset[start:end]

        # 序列化数据
        serializer = UserMarkSerializer(paginated_queryset, many=True)

        # 计算总条目数，用于分页信息
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size  # 向上取整

        # 构建分页结果
        response_data = {
            'count': total_count,
            'results': serializer.data,
            'total_pages': total_pages
        }

        return Response(response_data)

    def create(self, request):
        """
        收藏条目，用户可以添加备注和喜好等级
        """
        user = request.user
        mark_id = request.data.get('mark')
        note = request.data.get('note', "blank")
        preference_level = request.data.get('preference_level', 0)

        try:
            mark = Mark.objects.get(id=mark_id)
        except Mark.DoesNotExist:
            return Response({"detail": "Mark not found."}, status=status.HTTP_404_NOT_FOUND)

        user_mark, created = UserMark.objects.get_or_create(
            user=user,
            mark=mark,
            defaults={'note': note, 'preference_level': preference_level}
        )

        if not created:
            return Response({"detail": "Already bookmarked."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserMarkSerializer(user_mark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        更新收藏条目的备注或喜好等级
        """
        user = request.user
        try:
            user_mark = UserMark.objects.get(id=pk, user=user)
        except UserMark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserMarkSerializer(user_mark, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        删除收藏条目
        """
        user = request.user
        try:
            user_mark = UserMark.objects.get(id=pk, user=user)
        except UserMark.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        user_mark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
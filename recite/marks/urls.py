from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserProfileView, UserUpdateView, ChangePasswordView, MarkCollectionView, TagViewSet
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from marks import views

router = DefaultRouter()
router.register(r'marks', views.MarkViewSet, basename='mark')
router.register(r'user-marks', views.UserMarkViewSet, basename='user-mark')
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    # JWT Token obtain route
    path('login/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user-profile'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/password/change/', ChangePasswordView.as_view(), name='change-password'),
    path('collection/', MarkCollectionView.as_view(), name='mark-collection'), 
]
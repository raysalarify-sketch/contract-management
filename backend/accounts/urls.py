from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, SimpleLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('simple-login/', SimpleLoginView.as_view(), name='simple_login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

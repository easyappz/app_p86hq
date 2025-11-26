from django.urls import path
from .views import (
    HelloView,
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    ProfileView,
    MessagesListView,
    MessageCreateView
)

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("messages/", MessagesListView.as_view(), name="messages-list"),
    path("messages/create/", MessageCreateView.as_view(), name="messages-create"),
]

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="portfolios/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/new/", views.portfolio_create, name="portfolio_create"),
    path("dashboard/<int:pk>/edit/", views.portfolio_edit, name="portfolio_edit"),
    path("p/<str:slug>/", views.portfolio_detail, name="portfolio_detail"),
]

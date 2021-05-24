from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('', views.home, name="home"),
    path('buyingandselling/', views.buyingandselling, name="buyingandselling"),
    path('profile/<str:pk>/', views.profile, name="profile"),
    path('create_order/<str:pk>/', views.createOrder, name="create_order"),
    path('top_up/<str:pk>/', views.top_up, name="top_up"),
    path('top_up/', views.topup, name="topup"),
]
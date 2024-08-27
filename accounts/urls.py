from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegisterForm.as_view(), name="register"),
    path('login/', views.UserLoginView.as_view(), name="login"),
    path('logout/', views.logoutView.as_view(), name="logout"),
    path('profile/', views.UserBankAccountUpdateView.as_view(), name="profile"),
]
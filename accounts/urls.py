from django.urls import path

from . import views

app_name="accounts"
urlpatterns=[
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name="user_logout"),
    path('register/verify/', views.UserRegistrationVerifyCodeView.as_view(), name='register_verify_code'),
    path('login/verify/', views.UserLoginVerifyCodeView.as_view(), name='login_verify_code'),
    path('reset/', views.UserPasswordResetView.as_view(), name='user_reset_password'),
    path('reset/done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<uidb64>/<token>/',views.UserPasswordConfirmView.as_view(), name="password_reset_confirm"),
    path('confirm/complete/', views.UserPasswordResetCompleteView.as_view() ,name="password_reset_complete")
]
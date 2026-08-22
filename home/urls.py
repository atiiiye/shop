from django.urls import path
from . import views


app_name='home'
urlpatterns=[
    path('', views.HomeView.as_view(), name='home'),
    path('<slug:slug>', views.PorductDetailsViews.as_view(), name='product_detail'),
]
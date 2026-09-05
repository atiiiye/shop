from django.urls import path, include

from . import views

app_name='home'

bucketurls=[
    path('', views.BucketListView.as_view(), name='bucket'),
    path('download_obj/<path:key>/', views.DownloadBucketObjectView.as_view(), name='download_obj_bucket'),
    path('delete_obj/<path:key>/', views.DeleteBucketObjectView.as_view(), name='delete_obj_bucket'),
]
urlpatterns=[
    path('', views.HomeView.as_view(), name='home'),
    path('category/<slug:category_slug>', views.HomeView.as_view(), name='category_filter'),
    path('bucket/',include(bucketurls)),
    path('<slug:slug>', views.PorductDetailsViews.as_view(), name='product_detail'),
]
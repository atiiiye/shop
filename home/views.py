from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from products.models import Product, Category
from . import tasks


class HomeView(View):
    def get(self, request, category_slug=None):
        products = Product.objects.filter(available=True)
        categories = Category.objects.all()
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        return render(request, 'home/index.html', {"products": products, "categories": categories})


class PorductDetailsViews(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        return render(request, 'home/detail.html', {"product": product})


class BucketListView(View):
    template_name = 'home/bucket.html'

    def get(self, request):
        objects = tasks.get_all_bucket_objects()
        return render(request, self.template_name, {"objects": objects})


class DeleteBucketObjectView(View):
    def get(self, request, key):
        tasks.delete_object_task.delay(key)
        messages.success(request, 'You item will be deleted soon', 'info')
        return redirect('home:bucket')


class DownloadBucketObjectView(View):
    def get(self, request, key):
        tasks.download_object_task.delay(key)
        messages.success(request, 'You item will be downloaded soon', 'info')
        return redirect('home:bucket')

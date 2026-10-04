import datetime
import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from products.models import Product
from .cart import Cart
from .forms import CartAddForm, DiscountApplyForm
from .models import Order, OrderItem, DiscountCode


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'orders/cart.html', {'cart': cart})


class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    form_class = DiscountApplyForm

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/order.html', {'order': order, 'form': self.form_class})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return redirect('orders:order_detail', order.id)


class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        request.session['order_pay'] = {"order_id": order_id}
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": settings.ZP_MERCHANT_ID,
            "amount": order.get_total_price(),
            "description": f"{order.user} - {order.updated}",
            "metadata": {"mobile": request.user.phone_number, "email": request.user.email},
            "callback_url": 'http://127.0.0.1:8000/orders/verify/',
        }
        req = requests.post(url=settings.ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        authority = req.json()['data']['authority']

        if req.json()['data']['code'] == 100:
            return redirect(f"{settings.ZP_API_STARTPAY}/{authority}")
        else:
            messages.error(request, "Error! Something went wrong", "danger")
            return redirect("home:home")


class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session['order_pay']['order_id']
        order = get_object_or_404(Order, id=order_id)
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        if status == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json", }
            req_data = {
                "merchant_id": settings.ZP_MERCHANT_ID,
                "amount": order.get_total_price(),
                "authority": authority
            }
            verify_req = requests.post(settings.ZP_API_VERIFY, data=json.dumps(
                req_data), headers=req_header)

            if len(verify_req.json()["error"]) == 0 and verify_req.json()['data']['code'] == 100:
                order.paid = True
                order.save()
                messages.success(request, "Your order registered successfully", 'success')
                return redirect('home:home')
            else:
                error_code = verify_req.json()['errors']['code']
                error_message = verify_req.json()['errors']['message']
                messages.error(request, f"Error {error_code} ! {error_message}", "danger")
                return redirect('home:home')
        else:
            messages.error(request, "Error! Something went wrong", "danger")
            return redirect("home:home")


class DiscountApplyView(LoginRequiredMixin, View):
    form_class = DiscountApplyForm

    def post(self, request, order_id):
        now = datetime.datetime.now()
        form= self.form_class(request.POST)
        if form.is_valid():
            code= form.cleaned_data['code']
            try:
                discount= DiscountCode.objects.get(code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except DiscountCode.DoesNotExist:
                messages.error(request,'Code is invalid','danger')
                return redirect('orders:order_detail' , order_id)

            order=Order.objects.get(id=order_id)
            order.discount=discount.discount
            order.save()
            return redirect('orders:order_detail' , order_id)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.db import connection
import base64
import pickle

from .models import Product, Order, Coupon, ImportedOrder

# FLAW 1, Authentication Failures
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = User(username=username)
        user.set_password(password) # FLAW 1: user = User(username=username, password=password)
        user.save()

        return redirect("login")

    return render(request, "shopapp/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("search")

        return HttpResponse("Kirjautuminen epäonnistui")

    return render(request, "shopapp/login.html")

# FLAW 2, Injection
def search_products(request):
    query = request.GET.get("q", "")

    sql = (
        "SELECT id, name, price "
        "FROM shopapp_product "
        "WHERE name LIKE '%%%s%%'" % query
    )

    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(
        request,
        "shopapp/search.html",
        {"results": results, "query": query},
    )

# FLAW 3, IDOR
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    return render(
        request,
        "shopapp/order_detail.html",
        {"order": order},
    )

# FLAW 4, Insecure Design
def apply_coupon(request):
    code = request.GET.get("code", "")
    coupon = Coupon.objects.filter(code=code).first()

    if coupon:
        message = f"Kuponki {code} hyväksytty: {coupon.discount_percent}% alennus"
    else:
        message = "Kuponkia ei ole"

    return HttpResponse(message)

# FLAW 5, Software/Data Integrity Failures
def import_data(request):
    if request.method == "POST":
        encoded = request.POST.get("data", "")
        raw_bytes = base64.b64decode(encoded)

        obj = pickle.loads(raw_bytes)

        ImportedOrder.objects.create(raw_data=str(obj))
        return HttpResponse("Data tuotu")

    return render(request, "shopapp/import.html")

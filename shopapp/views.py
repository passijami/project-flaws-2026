from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.db import connection
import base64
import pickle
import json

from .models import Product, Order, Coupon, ImportedOrder

# FLAW 1, Cryptographic Failures
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = User(username=username, password=password)      # FIX FLAW 1
        user.save()                                            # user = User(username=username)
                                                               # user.set_password(password)
        return redirect("login")

    return render(request, "shopapp/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
                                                                # Password is compared directly with the plaintext
        user = User.objects.filter(
            username=username,
            password=password
        ).first()

        if user:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            return redirect("search")

        return HttpResponse("Kirjautuminen epäonnistui")

    return render(request, "shopapp/login.html")

# FLAW 2, Injection
def search_products(request):
    query = request.GET.get("q", "")

    sql = (                                    # FIX FLAW 2
        "SELECT id, name, price "              # sql = "SELECT id, name, price FROM shopapp_product WHERE name LIKE %s"
        "FROM shopapp_product "                # with connection.cursor() as cursor:
        "WHERE name LIKE '%%%s%%'" % query     #    cursor.execute(sql, [f"%{query}%"])
    )                                          #    results = cursor.fetchall()
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
    # FIX FLAW 3
    #if order.owner != request.user:
        #return HttpResponse("Käyttäjällä ei oikeutta nähdä tilausta!", status=403)
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
    # FIX FLAW 4
        #if request.user in coupon.used_by.all():
            #message = "Kuponki jo käytetty"
        #else:
            #coupon.used_by.add(request.user)
            #message = f"Kuponki {code} hyväksytty: {coupon.discount_percent}% alennus"
    #else:
        #message = "Kuponkia ei ole"

    return HttpResponse(message)

# FLAW 5, Software and Data Integrity Failures

def import_data(request):
    if request.method == "POST":
        encoded = request.POST.get("data", "")
        raw_bytes = base64.b64decode(encoded)
        obj = pickle.loads(raw_bytes)
        ImportedOrder.objects.create(raw_data=str(obj))
        return HttpResponse("Data tuotiin")

        # FIX FLAW 5
        #try:
             #obj = json.loads(raw_bytes)
        #except (json.JSONDecodeError, UnicodeDecodeError):
            #return HttpResponse("Virheellinen data", status=400)
        
        #ImportedOrder.objects.create(raw_data=str(obj))
        #return HttpResponse("Data tuotu")
    return render(request, "shopapp/import.html")

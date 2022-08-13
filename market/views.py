from django.shortcuts import render
from django.http import JsonResponse
from .models import Product

# Create your views here.


def insertProduct(request):
    if request.method == 'POST':

        try:
            product = Product.objects.create(
                code= request.POST['code'],
                name= request.POST['name'],
                price=int(request.POST['price']),
                inventory=int(request.POST['inventory'])
            )

            return JsonResponse({
                'id': product.id
            }, status=201)

        except:
            return JsonResponse({
                "message": "Duplicate code (or other messages)"
            }, status=400)

def productList(request):
    
    if request.method == 'GET':
        data = []

        search = request.GET.get('search', '')
        if search == '':
            products = Product.objects.all()
            for product in products:
                data.append({
                    'id': product.id,
                    'code': product.code,
                    'name': product.name,
                    'price': product.price,
                    'inventory': product.inventory,
                })

            return JsonResponse({
                'products': data,
            }, status=200)
        else:
            products = Product.objects.filter(name__contains=str(search))
            for product in products:
                data.append({
                    'id': product.id,
                    'code': product.code,
                    'name': product.name,
                    'price': product.price,
                    'inventory': product.inventory,     
                })

            return JsonResponse({
                'products': data
            }, status=200)


def prodcutInfo(requets, id):
    if requets.method == 'GET':
        try:
            product = Product.objects.get(code=id)
            return JsonResponse({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'inventory': product.inventory,
            }, status=200)
        except:
            return JsonResponse({
                'message': 'Product  Not Found.'
            }, status=404)
import json
from django.http import JsonResponse
from .models import Customer, Product, Order
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
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


@login_required()
def shoppingCart(request):
    customer = Customer.objects.get(user=request.user)
    order = customer.orders.get(status=1)
    data = list()
    for row in order.rows.all():
        data.append({
            'code': row.product.code,
            'name': row.product.name,
            'price': row.product.price,
            'amount': row.amount,
        })
    return JsonResponse({
        'total_price': order.total_price,
        'items': data,
    }, status=200)

# @login_required
def addItem(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        data = list()
        errors = list()

        for b in body:
            try:
                product = Product.objects.filter(code=b['code']).count() == 1, 'Product not found.'

                order = Order.objects.get(customer=request.user.customer, status=1)
                order.add_product(product, b['amount'])
                order.save()
                
                data.append({
                    'code': product.code,
                    'name': product.name,
                    'price': product.price,
                    'amount': order.rows.get(product=product).amount,
                })
            except AssertionError as msg:
                errors.append({
                    'code': b['code'],
                    'message': str(msg)
                })
            except ObjectDoesNotExist as msg:
                return JsonResponse({
                    'message': str(msg)
                })

        if errors == []:
            return JsonResponse({
                'items': data
            }, status=200)
    
        return JsonResponse({
            'errors': errors,
            'items': data
        }, status=404)

@login_required
def removeItem(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        listItems = list()
        errors = list()

        for b in body:
            try:
                assert Product.objects.filter(code=b['code']).count() == 1, 'Product not found'
                product = Product.objects.get(code=b['code'])
                order = Order.objects.get(customer=request.user.customer, status=1)
                assert order.rows.filter(product=product).count() == 1, 'Product not found in order_rows.'
                
                order.remove_product(product, b.get('amount', None))

                if order.rows.filter(product=product).count() == 1:
                    listItems.append({
                        'code': product.code,
                        'name': product.name,
                        'price': product.price,
                        'amount': order.rows.get(product=product).amount,
                    })
                
            except AssertionError as msg:
                errors.append({
                    'code': b['code'],
                    'message': str(msg)
                })
        
        if errors == []:
            return JsonResponse({
                'total_price': order.total_price,
                'items': listItems,
            }, status=200)
        
        return JsonResponse({
            'total_price': order.total_price,
            'errors': errors,
            'items': listItems,
        }, status=404)

@login_required
def submit(request):
    if request.method == 'POST':
        try:
            order = Order.objects.get(customer=request.user.customer, status=1)
            order.submit()

            data = list()

            for row in order.rows.all():
                data.append({
                    'code': row.product.code,
                    'name': row.product.name,
                    'price': row.product.price,
                    'amount': row.amount,
                })

            return JsonResponse({
                'id': order.id,
                'order_time': order.order_time,
                'status': 'submitted',
                'totoal_price': order.total_price,
                'rows': data,
            }, status=200)

        except AssertionError as msg:
            return JsonResponse({
                'message': str(msg)
            }, status=400)
        except ObjectDoesNotExist as msg:
            return JsonResponse({
                'message': str(msg)
            }, status=400)
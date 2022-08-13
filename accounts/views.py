from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from market.models import Customer
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

# Create your views here.

def registerCustomer(request):

    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                password = request.POST.get('password'),
                email = request.POST.get('email'),
                first_name = request.POST.get('first_name'),
                last_name = request.POST.get('last_name'),
            )

            customer = Customer.objects.create(
                user = user,
                phone = request.POST.get('phone'),
                address = request.POST.get('address')
            )

            return JsonResponse({
                'id': customer.id,
            }, status=201)

        except:
            return JsonResponse({
                'message': 'Username already exists. (or other messages)'
            }, status=400)
        

def customerList(request):
    if request.method == 'GET':
        
        search = request.GET.get('search', '')

        if search == '':
            customers = Customer.objects.all()
            data = list()
            for customer in customers:
                data.append({
                    'id': customer.id,
                    'username': customer.user.username,
                    'first_name': customer.user.first_name,
                    'last_name': customer.user.last_name,
                    'email': customer.user.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'balance': customer.balance,
                })

            return JsonResponse({
                'customers': data,
            }, status=200)

        else:
            customers = Customer.objects.filter(
                Q(user__username__contains=search) | Q(user__first_name__contains=search) | 
                Q(user__last_name__contains=search) | Q(address__contains=search)
            )
            data = list()
            for customer in customers:
                data.append({
                    'id': customer.id,
                    'username': customer.user.username,
                    'first_name': customer.user.first_name,
                    'last_name': customer.user.last_name,
                    'email': customer.user.email,
                    'phone': customer.phone,
                    'address': customer.address,
                    'balance': customer.balance,
                })

            return JsonResponse({
                'customers': data,
            }, status=200)

def customerInfo(request, id):
    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=id)
            return JsonResponse({
                'id': customer.id,
                'username': customer.user.username,
                'first_name': customer.user.first_name,
                'last_name': customer.user.last_name,
                'email': customer.user.email,
                'phone': customer.phone,
                'address': customer.address,
                'balance': customer.balance,
            }, status=200)
        except:
            return JsonResponse({
                'message': 'Customer Not Found.'
            }, status=404)

def customerEdit(request, id):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=id)

            if request.POST.get('password') or request.POST.get('username') or request.POST.get('id'):
                return JsonResponse({
                'message': "'Cannot edit customer's identity and credentials.'"
            }, status=403)

            customer.user.first_name = request.POST.get('first_name', customer.user.first_name)
            customer.user.last_name = request.POST.get('last_name', customer.user.last_name)
            customer.user.email = request.POST.get('email', customer.user.email)
            customer.address = request.POST.get('address', customer.address)
            customer.balance = request.POST.get('balance', customer.balance)
            customer.user.save()
            customer.save()

            return JsonResponse({
                'id': customer.id,
                'username': customer.user.username,
                'first_name': customer.user.first_name,
                'last_name': customer.user.last_name,
                'email': customer.user.email,
                'phone': customer.phone,
                'address': customer.address,
                'balance': customer.balance,  
            }, status=200)

        except:
            return JsonResponse({
                'message': 'Balance should be integer. (or other messages)'
            }, status=400)



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                'message': 'You are logged in successfully.'
            }, status=200)

        else:
            return JsonResponse({
                'message': 'Username or Password is incorrect.'
            }, status=404)

def logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            auth_logout(request)
            return JsonResponse({
                'message': 'You are logged out successfully.'
            }, status=200)
        
        return JsonResponse({
            'message': 'You are not logged in.'
        }, status=403)

def profile(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)

            return JsonResponse({
                'id': customer.id,
                'username': customer.user.username,
                'first_name': customer.user.first_name,
                'last_name': customer.user.last_name,
                'email': customer.user.email,
                'phone': customer.phone,
                'address': customer.address,
                'balance': customer.balance,
            }, status=200)
        
        return JsonResponse({
            'message': 'You are not logged in.'
        }, status=403)
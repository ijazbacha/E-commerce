from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse
from .models import product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.template.loader import get_template
from .utils import render_to_pdf



# Create your views here.
def index(request):
	#products = product.objects.all()
	#print(products)
	#n = len(products)
	#nslides = n//4 + ceil((n/4)-(n//4))
	#params = {'no-of-slides': nslides, 'range': range(1,nslides), 'product': products}
	#allprods = [[products, range(1,nslides), nslides], 
	#           [products, range(1,nslides), nslides]]
	#params = {'allprods': allprods} 

	allprods = []
	catprods = product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prod = product.objects.filter(category=cat)
		n = len(prod)
		nslides = n//4 + ceil((n/4)-(n//4))
		allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods}          
	return render(request, 'shop/index.html', params)


def handleSignup(request):
	if request.method == 'POST':
		username = request.POST['username']
		fname = request.POST['fname']
		lname = request.POST['lname']
		email = request.POST['email']
		pass1 = request.POST['pass1']
		pass2 = request.POST['pass2']

		#checks for invalid inputs
		if len(username)>10 or len(username)<5:
			messages.error(request, 'username must be 10 characters')
			return redirect('shophome')

		if not username.isalnum():
			messages.error(request, 'username should only contain letters and numbers')
			return redirect('shophome')

		if pass1 != pass2:
			messages.error(request, 'password do not match')
			return redirect('shophome')

		if len(pass1)<8 or len(pass1)>10:
			messages.error(request, 'password must be between 8 & 10')
			return redirect('shophome')

		#create user
		myuser = User.objects.create_user(username, email, pass1)
		myuser.first_name = fname
		myuser.last_name = lname
		myuser.save()
		messages.success(request, 'Your account has been successfully created please login to your account')
		return redirect('shophome')

	else:
		return HttpResponse('404 - Not Found')


def handleLogin(request):
	if request.method == 'POST':
		loginusername = request.POST['loginusername']
		loginpassword = request.POST['loginpassword']
		user = authenticate(username=loginusername, password=loginpassword)

		if user is not None:
			login(request, user)
			messages.success(request, 'successfully logged In')
			return redirect('shophome')
		else:
			messages.error(request, 'please enter correct password and username')
			return redirect('shophome')
	#return HttpResponse('404 - Not Found')
	return render(request, 'shop/login.html')



def handleLogout(request):
	
	logout(request)
	messages.success(request, 'successfully logged out')
	return redirect('shophome')

def searchMatch(query,item):
	if query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower() or query in item.desc.lower():
		return True
	else:
		return False


def search(request):
	query = request.GET.get('search')
	allprods = []
	catprods = product.objects.values('category', 'id')
	cats = {item['category'] for item in catprods}
	for cat in cats:
		prodtemp = product.objects.filter(category=cat)
		prod = [item for item in prodtemp if searchMatch(query, item)]
		n = len(prod)
		nslides = n//4 + ceil((n/4)-(n//4))
		if len(prod) != 0:
			allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods, 'msg': ""}
	if len(allprods) == 0 or len(query)<4:
		params = {'msg': "Please make sure to enter relavent search query"}          
	return render(request, 'shop/search.html', params)





def about(request):
	return render(request, 'shop/about.html')

def contect(request):
	if request.method == "POST":
		name  = request.POST.get('name', '')
		email = request.POST.get('email', '')
		phone = request.POST.get('phone', '')
		desc  = request.POST.get('desc', '')
		if len(name)<3 or len(email)<3 or len(phone)<3 or len(desc)<20:
			messages.error(request, 'Please fill the form correctly.')
		else:
			contact = Contact(name=name, email=email, phone=phone, desc=desc)
			contact.save()
			messages.success(request, 'Your message has been successfully sent.')
		#thank = True
		#return render(request, 'shop/contact.html', {'thank':thank,})
	return render(request, 'shop/contact.html')



def tracker(request):
	if request.method == "POST":
		orderId  = request.POST.get('orderId', '')
		email = request.POST.get('email', '')
		try:
			order = Orders.objects.filter(order_id=orderId, email=email)
			if len(order)>0:
				update = OrderUpdate.objects.filter(order_id=orderId)
				updates = []
				for item in update:
					updates.append({'text':item.update_desc, 'time':item.timestamp})
					response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
				return HttpResponse(response)
			else:
				return HttpResponse('{"status":"noitems"}')

		except Exception as e:
			return HttpResponse('{"status":"error"}')				
	return render(request, 'shop/tracker.html')



def prodView(request, myid):
	prod = product.objects.filter(id=myid)
	return render(request, 'shop/prodview.html', {'product':prod[0]})
'''
def checkout(request):
	if request.method == "POST":
		items_json = request.POST.get('itemsjson', '')
		name     = request.POST.get('name', '')
		amount     = request.POST.get('amount', '')
		email    = request.POST.get('email', '')
		address  = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
		city     = request.POST.get('city', '')
		state    = request.POST.get('state', '')
		zip_code = request.POST.get('zip_code', '')
		phone    = request.POST.get('phone', '')
		order = Orders(items_json=items_json, name=name, amount=amount, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone)
		order.save()
		update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
		update.save()
		thank = True
		id = order.order_id
		return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
		#return redirect('GeneratePDF')
		 #request paytm to tranfer amount to your account after payment by user

	return render(request, 'shop/checkout.html', locals())
'''

def GeneratePDF(request):
	order_id = request.session.get('order_id')
	order = get_object_or_404(Orders, pk=order_id)
	template = get_template('shop/invoice.html')
	context = {
		"Invoice_id": str(order_id),
		"customer_name": str(order.name),
		"amount": str(order.amount),
		"email": str(order.email),
		"address": str(order.address),
		"phone": str(order.phone),
		"today": "today"
		}
	html = template.render(context)
	pdf = render_to_pdf('shop/invoice.html', context)
	if pdf:
		return HttpResponse(pdf, content_type='application/pdf')
	return HttpResponse('Not Found')


@csrf_exempt
def payment_done(request):
	order_id = request.session.get('order_id')
	thank = True
	return render(request, 'shop/payment_done.html', {'thank':thank, 'order_id':order_id})
	#return redirect('GeneratePDF')
 
 
@csrf_exempt
def payment_cancelled(request):
    return render(request, 'shop/payment_cancelled.html')

@login_required(login_url="/shop/login/")
def checkout(request):
	if request.method == "POST":

		items_json = request.POST.get('itemsjson', '')
		name     = request.POST.get('name', '')
		amount     = request.POST.get('amount', '')
		email    = request.POST.get('email', '')
		address  = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
		city     = request.POST.get('city', '')
		state    = request.POST.get('state', '')
		zip_code = request.POST.get('zip_code', '')
		phone    = request.POST.get('phone', '')
		order = Orders(items_json=items_json, name=name, amount=amount, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone)
		order.save()
		update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
		update.save()
		thank = True
		id = order.order_id
		request.session['order_id'] = order.order_id
		return redirect('process_payment')
	return render(request, 'shop/checkout.html', locals())

def process_payment(request):
	order_id = request.session.get('order_id')
	order = get_object_or_404(Orders, pk=order_id)
	host = request.get_host()
 
	paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(order.amount),
        'item_name': 'Order {}'.format(order.name),
        'invoice': str(order),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }
    # Create the instance.
	form = PayPalPaymentsForm(initial=paypal_dict)
	context = {"form": form}
	return render(request, "shop/process_payment.html", context)


def manfashion(request):
	allprods = []
	subcate = ('man-shirts', 'Watch', 'Jacket', 'Shoes')
	catprods = product.objects.values('subcategory', 'id')
	cats = {item['subcategory'] for item in catprods}
	for cat in cats:
		for sub in subcate:
			if cat == sub:
				prod = product.objects.filter(subcategory=cat)
				n = len(prod)
				nslides = n//4 + ceil((n/4)-(n//4))
				allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods}          
	return render(request, 'shop/manfashion.html', params)


		


def girlfashion(request):
	allprods = []
	subcate = ('Girls_Watchs', 'Girls_Shirts', 'Jewellery', 'Girls_Shoes')
	catprods = product.objects.values('subcategory', 'id')
	cats = {item['subcategory'] for item in catprods}
	for cat in cats:
		for sub in subcate:
			if cat == sub:
				prod = product.objects.filter(subcategory=cat)
				n = len(prod)
				nslides = n//4 + ceil((n/4)-(n//4))
				allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods}          
	return render(request, 'shop/girlfashion.html', params)



def computer(request):
	allprods = []
	subcate = ('Laptop', 'Usb')
	catprods = product.objects.values('subcategory', 'id')
	cats = {item['subcategory'] for item in catprods}
	for cat in cats:
		for sub in subcate:
			if cat == sub:
				prod = product.objects.filter(subcategory=cat)
				n = len(prod)
				nslides = n//4 + ceil((n/4)-(n//4))
				allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods}          
	return render(request, 'shop/computer.html', params)



def electronic(request):
	allprods = []
	subcate = ('Heater', 'Tv')
	catprods = product.objects.values('subcategory', 'id')
	cats = {item['subcategory'] for item in catprods}
	for cat in cats:
		for sub in subcate:
			if cat == sub:
				prod = product.objects.filter(subcategory=cat)
				n = len(prod)
				nslides = n//4 + ceil((n/4)-(n//4))
				allprods.append([prod, range(1, nslides), nslides])
	params = {'allprods':allprods}          
	return render(request, 'shop/electronic.html', params)
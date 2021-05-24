from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Customer
import random
from django.core import serializers
import requests


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                bitcoin_wallet_value = Customer.objects.filter(name=user).values('bitcoin_wallet')
                for value in bitcoin_wallet_value:
                    wallet_balance = value['bitcoin_wallet']
                if wallet_balance == None:
                    welcome_bitcoin_gift = random.randint(1, 10)
                    Customer.objects.filter(name=user).update(bitcoin_wallet=welcome_bitcoin_gift)
                messages.success(request, 'Account created for ' + user)
                return redirect('home')

        context = {'form':form}
        return render(request, 'accounts/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    orders = Order.objects.all()
    buying = orders.filter(sellingorbuying='Buying', status='Available').count()
    selling = orders.filter(sellingorbuying='Selling', status='Available').count()
    automatic_sale = serializers.serialize("python", Order.objects.all())

    customers = Customer.objects.all()
    bitcoin_wallet_value = Customer.objects.filter(user=request.user).values('bitcoin_wallet')
    get_customer_id = Customer.objects.filter(user=request.user).values('id')
    eur_wallet = Customer.objects.filter(user=request.user).values('fiat_wallet')

    customer_id = 0
    wallet_balance = 0
    eur_wallet_balance = 0


    for id in get_customer_id:
        customer_id = id['id']

    for value in bitcoin_wallet_value:
        wallet_balance = value['bitcoin_wallet']

    for eur in eur_wallet:
        eur_wallet_balance = eur['fiat_wallet']

    automatic_sale_data = [[order['pk'], order['fields']['btc_value'], order['fields']['eur_value'], order['fields']['sellingorbuying'], order['fields']['status'], order['fields']['customer']] for order in automatic_sale]
    automatic_sale_data_comparison = [[order['pk'], order['fields']['btc_value'], order['fields']['eur_value'], order['fields']['sellingorbuying'], order['fields']['status'], order['fields']['customer']] for order in automatic_sale]

    best_buyer={"id_seller" : [], "id_selling_order" : [], "id_buyer" : [], "eur" : []}
    for order in automatic_sale_data:
        for order_comparison in automatic_sale_data_comparison:
            if order[0] !=  order_comparison[0]:
                if order[3] == 'Buying':
                    if order_comparison[3] == 'Selling':
                        if order[4] == 'Available':
                            if order_comparison[4] == 'Available':
                                if order[1] <= order_comparison[1]:
                                    if order[2] >= (order_comparison[2] * order[1] / order_comparison[1]):
                                        if order_comparison[5] not in best_buyer["id_seller"]:
                                            best_buyer["id_seller"].append(order_comparison[5])
                                        if order_comparison[0] not in best_buyer["id_selling_order"]:
                                            best_buyer["id_selling_order"].append(order_comparison[0])
                                        best_buyer["id_buyer"].append(order[5])
                                        best_buyer["eur"].append(order[2])

    if best_buyer['eur']:
        for item in automatic_sale_data:
            if item[2] == sorted(best_buyer['eur'])[-1]:
                if item[5] in best_buyer['id_buyer']:
                    for id in best_buyer['id_selling_order']:
                        selling_order_id = id
                    for id in best_buyer['id_seller']:
                        seller_id = id
                    order_for_sale_btc = Order.objects.filter(id=selling_order_id).values('btc_value')
                    for value in order_for_sale_btc:
                        order_for_sale_btc_value = value['btc_value']
                    Order.objects.filter(id=item[0]).update(status='Sold')
                    Order.objects.filter(id=selling_order_id).update(btc_value=order_for_sale_btc_value - item[1])
                    order_for_sale_eur = Order.objects.filter(id=selling_order_id).values('eur_value')
                    for value in order_for_sale_eur:
                        order_for_sale_eur_value = value['eur_value']
                    Order.objects.filter(id=selling_order_id).update(eur_value=order_for_sale_eur_value - (order_for_sale_eur_value / order_for_sale_btc_value * item[1]))
                    btc_buyer_wallet = Customer.objects.filter(id=item[5]).values('bitcoin_wallet')
                    eur_buyer_wallet = Customer.objects.filter(id=item[5]).values('fiat_wallet')
                    for value in btc_buyer_wallet:
                        BTC_buyer_wallet = value['bitcoin_wallet']
                    for value in eur_buyer_wallet:
                        EUR_buyer_wallet = value['fiat_wallet']
                    Customer.objects.filter(id=item[5]).update(bitcoin_wallet=BTC_buyer_wallet + item[1])
                    Customer.objects.filter(id=item[5]).update(fiat_wallet=EUR_buyer_wallet - item[2])
                    btc_seller_wallet = Customer.objects.filter(id=seller_id).values('bitcoin_wallet')
                    eur_seller_wallet = Customer.objects.filter(id=seller_id).values('fiat_wallet')
                    for value in btc_seller_wallet:
                        BTC_seller_wallet = value['bitcoin_wallet']
                    for value in eur_seller_wallet:
                        EUR_seller_wallet = value['fiat_wallet']
                    Customer.objects.filter(id=seller_id).update(bitcoin_wallet=BTC_seller_wallet - item[1])
                    Customer.objects.filter(id=seller_id).update(fiat_wallet=EUR_seller_wallet + item[2])
    for order in automatic_sale_data:
        if order[1] == 0:
            Order.objects.filter(id=order[0]).update(status='Sold')


    context = {'orders': orders, 'customers': customers, 'customer_id': customer_id, 'wallet_balance': wallet_balance,  'buying': buying,
               'selling': selling, 'eur_wallet_balance' : eur_wallet_balance}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def buyingandselling(request):
    loss_and_profit_data = serializers.serialize("python", Order.objects.all())

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    params = {
        'start': '1',
        'limit': '3',
        'convert': 'EUR'
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "85f542f7-9b2d-42e5-836b-a6c4971f51af"
    }

    r = requests.get(url=url, headers=headers, params=params).json()

    for currency in r['data']:
        if currency['symbol'] == 'BTC':
            BTC_current_price = currency["quote"]["EUR"]["price"]

    loss_and_profit = [[order['fields']['customer'], order['fields']['btc_value'], order['fields']['eur_value'], order['fields']['status']] for order in loss_and_profit_data]

    profit = 0
    loss = 0

    for order in loss_and_profit:
        if order[3] == 'Sold':
            if order[0] == request.user.customer.id:
                if order[2] < (order[1] * BTC_current_price):
                    profit = (order[1] * BTC_current_price) - order[2]
                if order[2] > (order[1] * BTC_current_price):
                    loss = order[2] - (order[1] * BTC_current_price)

    context = { 'BTC_current_price': BTC_current_price, 'profit': profit, 'loss': loss  }
    return render(request, 'accounts/buyingandselling.html', context)


@login_required(login_url='login')
def profile(request, pk):
    customer = Customer.objects.get(id=pk)

    context = {'customer': customer}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def top_up(request, pk):
    customer = Customer.objects.get(id=pk)

    context = {'customer': customer}
    return render(request, 'accounts/top_up.html', context)


@login_required(login_url='login')
def topup(request):
    topupvalue = request.GET["topupvalue"]
    eur_wallet = Customer.objects.filter(user=request.user).values('fiat_wallet')
    for eurwallet in eur_wallet:
        eur_wallet_to_top_up = eurwallet['fiat_wallet']
    fiatwalletaftertopup = int(eur_wallet_to_top_up) + int(topupvalue)
    Customer.objects.filter(user=request.user).update(fiat_wallet=fiatwalletaftertopup)
    return redirect('/')

    context = {'eur_wallet' : eur_wallet}
    return render(request, 'accounts/topup.html', context)

@login_required(login_url='login')
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'sellingorbuying', 'btc_value', 'eur_value'), extra=1)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    bitcoin_wallet_balance = Customer.objects.filter(user=request.user).values('bitcoin_wallet')
    eur_wallet_balance = Customer.objects.filter(user=request.user).values('fiat_wallet')
    for value in bitcoin_wallet_balance:
        btc_balance = value['bitcoin_wallet']
    for value in eur_wallet_balance:
        eur_balance = value['fiat_wallet']
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            for field in formset:
                cleaneddata = field.cleaned_data
                bitcoin_balance = cleaneddata.get('btc_value')
                euro_balance = cleaneddata.get('eur_value')
                if cleaneddata.get('sellingorbuying') == 'Selling':
                    if int(bitcoin_balance) <= int(btc_balance):
                        formset.save()
                        return redirect('/')
                if cleaneddata.get('sellingorbuying') == 'Buying':
                    if int(euro_balance) <= int(eur_balance):
                        formset.save()
                        return redirect('/')
            messages.info(request, 'You don\'t have enough BTC or EURO in your wallets')

    context = {'formset': formset}
    return render(request, 'accounts/order_form.html', context)


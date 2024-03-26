from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
import logging
from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages
from .models import *
from docxtpl import DocxTemplate
from django.contrib import auth
import io
import datetime
import locale
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .forms import *
from django.contrib import messages
import datetime
from django.db.models import Sum


def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='secretary').exists():
                return redirect('index')
            elif user.groups.filter(name='manager').exists():
                return redirect('manager_main')
            else:
                return redirect('login')
        else:
            return render(request, 'login_page.html', {'error': 'Неправильное имя пользователя или пароль'})
    else:
        return render(request, 'login_page.html')

def forgot_pw(request):
    return render(request, 'forgot_pw.html')

def logout_page(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='secretary').exists())
def index(request):
    return render(request, 'index.html', {'username': auth.get_user(request).username})

def manager_main(request):
    name_query = request.GET.get('name', '')  # Получение значения фильтрации по дате

    products = Product.objects.all()

    if name_query:
        # Фильтрация студентов по дате сдачи
        products = products.filter(name__icontains=name_query)

    context = {
        'username': auth.get_user(request).username,
        'products': products,
        'name_query': name_query  # Передача значения фильтрации по дате в контекст
    }
    return render(request, 'manager_main.html', context)

def manager_product_page(request, id):
    product = get_object_or_404(Product, id=id)

    context = {
        'username': auth.get_user(request).username,
        'product': product,
        # 'defense_form': defense_form
    }

    return render(request, 'manager_product_page.html', context)

product_ids = []

def products(request):
    name_query = request.GET.get('name', '')  # Получение значения фильтрации по дате

    products = Product.objects.all()
    global product_ids
    product_ids = [i.id for i in products]

    if name_query:
        # Фильтрация студентов по дате сдачи
        products = products.filter(name__icontains=name_query)

    context = {
        'username': auth.get_user(request).username,
        'products': products,
        'name_query': name_query  # Передача значения фильтрации по дате в контекст
    }

    # Отправка значения фильтрации по дате обратно на страницу
    # чтобы сохранить введенную дату в поле поиска
    context['name_query'] = name_query

    # return HttpResponse(f"айдишки: {product_ids}")
    return render(request, 'products.html', context)

def product_page(request, id):
    product = get_object_or_404(Product, id=id)

    context = {
        'username': auth.get_user(request).username,
        'product': product,
        # 'defense_form': defense_form
    }

    return render(request, 'product_page.html', context)

def providers_list(request):
    providers = Provider.objects.all()
    context = {
        'username': auth.get_user(request).username,
        'providers': providers
    }
    return render(request, 'provider_list.html', context)

def provider_page(request, id):
    provider = get_object_or_404(Provider, id=id)
    comings = Coming_add.objects.filter(com_id__prov_id=provider).select_related('com_id').order_by('-com_id__date')

    context = {
        'username': auth.get_user(request).username,
        'provider': provider,
        'comings': comings,
    }

    return render(request, 'provider_page.html', context)

def recipient_list(request):
    recipients = Recipient.objects.all()
    context = {
        'username': auth.get_user(request).username,
        'recipients': recipients
    }
    return render(request, 'recipient_list.html', context)

def recipient_page(request, id):
    recipient = get_object_or_404(Recipient, id=id)
    expenditures = Expenditure_add.objects.filter(exp_id__rec_id=recipient).select_related('exp_id').order_by('-exp_id__date')

    context = {
        'username': auth.get_user(request).username,
        'recipient': recipient,
        'expenditures': expenditures,
    }

    return render(request, 'recipient_page.html', context)

inventory_ids = []

def inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            reason = form.cleaned_data['reason']
            
            try:
                
                # Проверяем наличие достаточного количества товара для списания
                if product.quantity >= quantity:
                    # Выполняем списание
                    product.quantity -= quantity
                    product.save()
                    
                    offs = Offs(product_id=product, quantity=quantity, reason=reason, created_at=datetime.date.today())
                    offs.save()
                    
                    return redirect('inventory')
                else:
                    return render(request, 'inventory.html', {'form': form, 'error_message': 'Недостаточно товара на складе'})
            except Product.DoesNotExist:
                return render(request, 'inventory.html', {'form': form, 'error_message': 'Товар не найден'})
    else:
        form = InventoryForm()

    date_query = request.GET.get('date')  # Получение значения фильтрации по дате

    if date_query:
        try:
            date_query = datetime.datetime.strptime(date_query, '%Y-%m-%d').date()
        except ValueError:
            date_query = None

    offs_list = Offs.objects.filter(created_at=date_query).order_by('-created_at') if date_query else Offs.objects.all().order_by('-created_at')
    global inventory_ids
    inventory_ids = [i.id for i in offs_list]

    context = {
        'username': auth.get_user(request).username,
        'form': form,
        'products': products,
        'offs_list': offs_list,
        'date_query': date_query,
        'error_message': ''
    }

    return render(request, 'inventory.html', context)

shipment_ids = []

def shipment(request):
    expenditures = Expenditure_add.objects.all().order_by('-exp_id__date')  # Получить все записи о списаниях
    global shipment_ids
    shipment_ids = [i.id for i in expenditures]
    if request.method == 'POST':
        expenditure_form = ExpenditureForm(request.POST)
        expenditure_add_form = ExpenditureAddForm(request.POST)
        print(request.user)
        if expenditure_form.is_valid() and expenditure_add_form.is_valid():
            secretary = get_object_or_404(Secretary, user=request.user)
            expenditure = expenditure_form.save(commit=False)
            expenditure.sec_id = secretary
            expenditure.date = date.today()
            expenditure.save()
            expenditure_add = expenditure_add_form.save(commit=False)
            expenditure_add.exp_id = expenditure
            expenditure_add.save()
            
            product_id = expenditure_add.product_id_id
            quantity_used = expenditure_add.quantity
            product = Product.objects.get(pk=product_id)
            product.quantity -= quantity_used
            product.save()

            messages.success(request, 'Данные успешно отправлены.')
            return redirect('shipment')
    else:
        expenditure_form = ExpenditureForm(initial={'sec_id': request.user.id, 'date': date.today()})
        expenditure_add_form = ExpenditureAddForm()

    context = {
        'username': auth.get_user(request).username,
        'expenditure_form': expenditure_form, 
        'expenditure_add_form': expenditure_add_form,
        'expenditures': expenditures
    }

    return render(request, 'shipment.html', context)

coming_ids = []

def coming(request):
    coming = Coming_add.objects.all().order_by('-com_id__date')
    global coming_ids
    coming_ids = [i.id for i in coming]
    if request.method == 'POST':
        coming_form = ComingForm(request.POST)
        coming_add_form = ComingAddForm(request.POST)
        if coming_form.is_valid() and coming_add_form.is_valid():
            secretary = get_object_or_404(Secretary, user=request.user)
            coming = coming_form.save(commit=False)
            coming.sec_id = secretary
            coming.save()
            coming_add = coming_add_form.save(commit=False)
            coming_add.com_id = coming
            coming_add.save()

            product_id = coming_add.product_id_id
            quantity_added = coming_add.quantity
            product = Product.objects.get(pk=product_id)
            product.quantity += quantity_added
            product.save()

            return redirect('coming')
    else:
        coming_form = ComingForm(initial={'sec_id': request.user.id, 'date': date.today()})
        coming_add_form = ComingAddForm()

    return render(request, 'coming.html', {'coming_form': coming_form, 'coming_add_form': coming_add_form, 'coming': coming, 'username': auth.get_user(request).username,})

def download_coming_report(request):
    doc = DocxTemplate("warehouse/static/coming_report.docx")
    secretary = get_object_or_404(Secretary, user=request.user)
    secretary_full_name = secretary.lastname + ' ' + secretary.name + ' ' + secretary.middlename
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()

    global coming_ids
    comings = []
    countfirst = 0

    sumcount = 0
    sumprice = 0

    for coming_id in coming_ids:
        # coming = get_object_or_404(Coming, id=coming_id)
        coming_add = get_object_or_404(Coming_add, id=coming_id)
        countfirst += 1
        summa = coming_add.quantity * coming_add.price
        sumcount += coming_add.quantity
        sumprice += summa

        comings.append({
            'date': coming_add.com_id.date,
            'contract': coming_add.com_id.contract_number,
            'recipient': coming_add.com_id.prov_id,
            "product": coming_add.product_id,
            "quantity": coming_add.quantity,
            "price": coming_add.price,
            "summa": summa,
        })


    context = {
        "secretary": secretary_full_name,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "comings": comings,
        "sumcount": sumcount,
        "sumprice": sumprice
    }
    doc.render(context)

    doc.save("report_coming.docx")
    doc_name = "report_coming.docx"

    # Создать HTTP-ответ, который будет содержать созданный документ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response

def download_shipment_report(request):
    doc = DocxTemplate("warehouse/static/shipment_report.docx")
    secretary = get_object_or_404(Secretary, user=request.user)
    secretary_full_name = secretary.lastname + ' ' + secretary.name + ' ' + secretary.middlename
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()

    global shipment_ids
    shipments = []
    countsecond = 0

    sumcount = 0
    sumprice = 0

    for shipment_id in shipment_ids:
        # coming = get_object_or_404(Coming, id=coming_id)
        shipment_add = get_object_or_404(Expenditure_add, id=shipment_id)
        countsecond += 1
        summa = shipment_add.quantity * shipment_add.price
        sumcount += shipment_add.quantity
        sumprice += summa

        shipments.append({
            'date': shipment_add.exp_id.date,
            'contract': shipment_add.exp_id.contract_number,
            'recipient': shipment_add.exp_id.rec_id,
            "product": shipment_add.product_id,
            "quantity": shipment_add.quantity,
            "price": shipment_add.price,
            "summa": summa,
        })

    context = {
        "secretary": secretary_full_name,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "shipmentss": shipments,
        "sumcount": sumcount,
        "sumprice": sumprice
    }
    doc.render(context)

    doc.save("report_shipment.docx")
    doc_name = "report_shipment.docx"

    # Создать HTTP-ответ, который будет содержать созданный документ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response

def download_inventory_report(request):
    doc = DocxTemplate("warehouse/static/inventory_report.docx")
    secretary = get_object_or_404(Secretary, user=request.user)
    secretary_full_name = secretary.lastname + ' ' + secretary.name + ' ' + secretary.middlename
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()

    global inventory_ids
    inventories = []
    countthird = 0

    for inventory_id in inventory_ids:
        inventory = get_object_or_404(Offs, id=inventory_id)
        countthird += 1

        inventories.append({
            'id': inventory.product_id.id,
            'name': inventory.product_id.name,
            'quantity': inventory.quantity,
            "reason": inventory.reason,
            "date": inventory.created_at,
        })

    context = {
        "secretary": secretary_full_name,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "inventories": inventories,
    }
    doc.render(context)

    doc.save("report_inventory.docx")
    doc_name = "report_inventory.docx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response

def download_material_report(request):
    doc = DocxTemplate("warehouse/static/material_report.docx")
    secretary = get_object_or_404(Secretary, user=request.user)
    secretary_full_name = secretary.lastname + ' ' + secretary.name + ' ' + secretary.middlename
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()
    start_of_month = current_time.replace(day=1)


    global product_ids
    products = []
    countforth = 0

    allinstart = 0
    allcoming = 0
    allshipment = 0
    allinventory = 0
    allquantity = 0

    for product_idd in product_ids:
        product = get_object_or_404(Product, id=product_idd)
        countforth += 1

        offs = Offs.objects.all()
        inventory_count = 0
        for i in offs:
            if i.product_id_id  == product_idd:
                inventory_count+=i.quantity
        allinventory += inventory_count

        print(inventory_count)

        coming = Coming_add.objects.all()
        coming_count = 0
        for i in coming:
            if i.product_id_id  == product_idd:
                coming_count+=i.quantity
        allcoming += coming_count
        
        print(coming_count)

        shipment = Expenditure_add.objects.all()
        shipment_count = 0
        for i in shipment:
            if i.product_id_id  == product_idd:
                shipment_count+=i.quantity
        allshipment += shipment_count

        print(shipment_count)

        # Находим сумму поставок на начало месяца
        coming_quantity = Coming_add.objects.filter(com_id__date__lte=start_of_month).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        
        # Находим сумму расходов на начало месяца
        expenditure_quantity = Expenditure_add.objects.filter(exp_id__date__lte=start_of_month).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        
        # Находим сумму списаний на начало месяца
        offs_quantity = Offs.objects.filter(created_at__lte=start_of_month).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        
        # Общее количество материалов на начало месяца
        instart_quantity = coming_quantity - expenditure_quantity - offs_quantity
        allinstart += instart_quantity
    
        allquantity += product.quantity

        print(instart_quantity)

        products.append({
            'id': product.id,
            'name': product.name,
            'instart': instart_quantity,
            "coming": coming_count,
            "shipment": shipment_count,
            "inventory": inventory_count,
            "quantity": product.quantity,
        })


    context = {
        "secretary": secretary_full_name,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "productss": products,
        "allinstart": allinstart,
        "allcoming": allcoming,
        "allshipment": allshipment,
        "allinventory": allinventory,
        "allquantity": allquantity,
    }
    doc.render(context)

    doc.save("report_material.docx")
    doc_name = "report_material.docx"

    # Создать HTTP-ответ, который будет содержать созданный документ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response
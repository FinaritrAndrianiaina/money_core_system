from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,logout,login
from django.http import FileResponse,HttpResponse
from django.contrib.auth.decorators import login_required
from manager.form import RegistrationForm,AccountAuthenticationForm,NewTransactionForm,AccountUpdateForm
from manager.models import Token
from django.db.models import Sum
from qrcode import QRCode
import io
from django import forms
import manager.backend_connector as b
# Create your views here.
def main_manager(request):
    return render(request,'main_manager.py')

def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email,password=raw_password)
            login(request,account)
            return redirect('home')
        else:
            context['form'] = form
    else:
        form = RegistrationForm()
        context['form'] = form
    return render(request,'register.html',context)


@login_required
def home(request):
    return render(request,'index.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email,password=password)

            if user:
                login(request,user)
                return redirect("home")
            
    else:
        form = AccountAuthenticationForm()
    
    context['login_form'] = form

    return render(request,'login.html',context=context)

@login_required
def create_get_new_adress(request):
    new_adress = b.create_new_adress()
    token = Token(account=request.user,priv_key=new_adress['priv_key'],token=new_adress['token'],balance=new_adress['balance'])
    token.save()
    return HttpResponse(content=bytes(token.token,'utf-8'))

@login_required
def new_transaction(request,token_id):
    if request.method == 'POST':
        _token = Token.objects.get(id=token_id)
        form = NewTransactionForm(request.POST)
        if form.is_valid():
            receiver_token = form.cleaned_data['receiver']
            amount = form.cleaned_data['amount']
            token = _token.token
            private_key = _token.priv_key
            m  = b.new_transaction(
                token = token,
                receiver_token=receiver_token,
                amount=amount,
                priv_key = private_key
            )
            messages.success(request,m['message'])
            return redirect('home')

@login_required
def tokenlist(request):
    token = Token.objects.filter(account=request.user)
    context = {}
    context['tokens'] = token
    return render(request,'component/tokenlist.htm',context)

@login_required
def update_form(request):
    my_token = Token.objects.filter(account=request.user)
    balance = my_token.aggregate(Sum('balance'))
    token_count = my_token.count()
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST,instance=request.user)
        try:
            form.clean_username()
            if form.is_valid():
                form.save()
        except forms.ValidationError:
            pass
        return redirect('home')
    else: 
        form = AccountUpdateForm(initial={'username':request.user.username})
    context = dict()
    context['u_form'] = form
    context['balance'] = balance['balance__sum']
    context['adresse'] = token_count
    context['email'] = request.user.email
    return render(request,'component/info.htm',context=context)

@login_required
def filedetail(request,token_id):
    a =QRCode()
    _token = Token.objects.get(id=token_id)
    a.add_data([_token.token, _token.priv_key],optimize=128)
    file = io.BytesIO()
    a.make_image().save(file)
    file.seek(0)
    response = FileResponse(streaming_content=(file), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename={_token.token}.png'
    return response

@login_required
def share_adress(request,token_id):
    a =QRCode()
    _token = Token.objects.get(id=token_id)
    a.add_data([_token.token],optimize=256)
    file = io.BytesIO()
    a.make_image().save(file)
    file.seek(0)

    response = FileResponse(streaming_content=(
        file), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename={_token.token}.png'
    return response

@login_required
def update_my_account(request):
    count = 0
    token_list = Token.objects.filter(account=request.user.id)
    for token in token_list:
        t = b.get_address(token.token)
        try:
            if not (int(t['balance']) == token.balance):
                token.balance = int(t['balance'])
                token.save()
                count += 1
        except:
            token.delete()
            return HttpResponse(bytes(t['message'],'utf-8'))
           
    return HttpResponse(bytes(f'{count} address updated','utf-8'))

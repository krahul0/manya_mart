from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth

from django.http import HttpResponse

#email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.models import Cart
from cart.views import _cart_id

from cart.models import CartItem
import requests


def register(request):

    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,
                                             email=email,username=username,password=password)
            user.phone_number=phone_number
            user.save()

            current_site=get_current_site(request)#current domain which is being used
            mail_subject='please activate your account'

            #content which will be sent in the email bodyor email body
            message=render_to_string('accounts/account_verification_email.html',
                                     {   #user object
                                         'user':user,
                                         #current domain
                                         'domain':current_site,
                                         #encoding the user id to prevent access from others
                                         'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                         #create token of user
                                         'token':default_token_generator.make_token(user),
                                     }
                                     )
            #email to which the message will be sent n it can be multiple messages
            to_email=email
            #parameters required for sendig mail
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            #messages.success(request,'sent verification email ')
            return redirect('/accounts/login/?command=verify&email='+email)
    else:
        form=RegistrationForm()

    context={
        'form':form,
         }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']

        user=auth.authenticate(email=email,password=password)

        if user is not None:
            try:

                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    #getting product variation by cart id
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variation.all()
                        product_variation.append(list[variation])

                    #get cart items from user to access his product varation
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    #product_variation=[1,2,3,4,5]
                    #ex_var_list=[1,2,3,4,5]
                    #to get similar values from both lists
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            # assign user to cart item
                            for item in cart_item:
                                item.user=user
                                item.save()


            except:
                pass
            auth.login(request,user)
            messages.success(request,'you are logged in')
            url=request.META.get('HTTP_REFERER')

            try:
                query=requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)

            except:
                 return redirect('dashboard')

        else:
            messages.error(request,'Invalid email or password')
            return redirect('login')

    return render(request,'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out')
    return redirect('login')

def activate(request, uidb64,token):
    try:
        #decode the uidb and store it in uid which will have pk
        uid=urlsafe_base64_decode(uidb64).decode()
        #return user object
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    #token is sed to extract the user
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'congratulations you can login now')
        return redirect('login')
    else:
        messages.error(request,'invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgot_password(request):
    if request.method=='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__iexact=email)

             #reset password
            current_site=get_current_site(request)#current domain which is being used
            mail_subject='please reset your account password'


            message=render_to_string('accounts/reset_password_email.html',
                                     {
                                         #user object
                                         'user':user,
                                         #current domain
                                         'domain':current_site,
                                         #encoding the user id to prevent access from others
                                         'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                         #create token of user
                                         'token':default_token_generator.make_token(user),
                                     }
                                     )
            #email to which the message will be sent n it can be multiple messages
            to_email=email
            #parameters required for sendig mail
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'password reset email is sent to your email')
            return redirect('login')

        else:
            messages.error(request,'account dosent exist')
            return redirect('forgot_password')
    return render(request,'accounts/forgot_password.html')

def resetpassword_validate(request, uidb64,token):
    try:
        #decode the uidb and store it in uid which will have pk
        uid=urlsafe_base64_decode(uidb64).decode()
        #return user object
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request,'session expired')
        return redirect('login')

def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password==confirm_password:
                   uid= request.session['uid']
                   user=Account.objects.get(pk=uid)
                   user.set_password(password)
                   user.save()
                   messages.success(request,'password reset done')
                   return redirect('login')

        else:
            messages.error(request,'password dosent match')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')








     # return HttpResponse('hi')
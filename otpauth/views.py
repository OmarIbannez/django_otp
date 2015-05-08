from django.shortcuts import render
from otpauth.models import OtpUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import pyotp
import pyqrcode
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def register(request):
    if request.method == 'POST':
        data = request.POST

        try:
            user =  User.objects.create_user(
                username = data['username'],
                password = data['password']
            )
            user.save()

        except Exception, e:
            return HttpResponse(e)

        otpuser = OtpUser(user = user)
        otpuser.save()

        return HttpResponseRedirect('/success')

    return render_to_response('register.html', {}, context_instance=RequestContext(request))

def auth_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        otpuser = OtpUser.objects.get(user__username=username)
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if otpuser.secret_key:
                    return HttpResponseRedirect('/otplogin')

                return HttpResponseRedirect('/success')

        return HttpResponseRedirect('/login')

    return render_to_response('login.html', {}, context_instance=RequestContext(request))

@login_required
def register_device(request):
    if request.method == 'POST':
        secret_key = request.POST['secret_key']
        otp = request.POST['otp']
        totp = pyotp.TOTP(secret_key)
        
        if totp.verify(otp) is False:
            logout(request)
            return HttpResponseRedirect('/login')
        
        otpuser = OtpUser.objects.get(user__username=request.user.username)
        otpuser.secret_key = secret_key
        otpuser.save()
        logout(request)
        return HttpResponseRedirect('/login')

    secret_key = pyotp.random_base32()
    username = request.user.username
    key_uri = 'otpauth://totp/appname:'+username+'?secret='+secret_key+'&issuer=appname'
    qr = pyqrcode.create(key_uri)
    qr_name = secret_key+'.svg'
    qr_file = os.path.join(BASE_DIR, 'static')+'/'+qr_name
    qr.svg(qr_file)

    return render_to_response('register_device.html', {'qr_file':qr_name, 'secret_key': secret_key}, context_instance=RequestContext(request))
    

@login_required
def otp_login(request):
    if request.method == 'POST':
        otpuser = OtpUser.objects.get(user__username=request.user.username)
        otp = request.POST['otp']
        totp = pyotp.TOTP(otpuser.secret_key)
        
        if totp.verify(otp) is False:
            logout(request)
            return HttpResponseRedirect('/login')
        
        return HttpResponseRedirect('/success')

    return render_to_response('otp_login.html', {}, context_instance=RequestContext(request))

@login_required
def success(request):
    return render_to_response('success.html', {}, context_instance=RequestContext(request))

@login_required
def auth_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')
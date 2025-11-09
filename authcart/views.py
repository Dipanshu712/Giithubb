from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.conf import settings
from django.views import View
from .utils import generate_token 


# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        username = request.POST['register_username']
        email = request.POST['register_email']
        password = request.POST['register_password']

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('/auth/signup/')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('/auth/signup/')

        # Create inactive user
        myuser = User.objects.create_user(username=username, email=email, password=password)
        myuser.is_active = False
        myuser.save()

        # Prepare activation email
        email_subject = "Activate Your Account"
        message = render_to_string('authentication/activate.html', {
            'user': myuser,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )
        email_message.send()

        messages.success(request, "Account created successfully! Check your email to activate your account.")
        return redirect('/auth/login/')

    # GET request renders signup page
    return render(request, "authentication/signup.html")


# ---------------- LOGIN ----------------
def handlelogin(request):
    if request.method == "POST":
        email = request.POST['login_email']
        password = request.POST['login_password']

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('/auth/login/')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('/')
            else:
                messages.warning(request, "Please activate your account first.")
                return redirect('/auth/login/')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('/auth/login/')

    return render(request, "authentication/login.html")


# ---------------- ACTIVATE ACCOUNT ----------------
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully! You can now log in.")
            return redirect('/auth/login/')
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return render(request, "authentication/activatefail.html")


# ---------------- LOGOUT ----------------
def handlelogout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('/auth/login/')

from django.urls import path
from authcart import views
from .views import ActivateAccountView


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.handlelogin, name='login'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate')
]


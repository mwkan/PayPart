from django.urls import path
from . import views

urlpatterns = [
    path('', views.start_payment_process, name='start_payment_process'),
    # Add more paths for other views in your app here
]

from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_payment_process, name='start_payment_process'),
    path('even_split/', views.even_split, name='even_split'),
    path('custom_split/', views.custom_split, name='custom_split'),
    # Add more paths for other views in your app here
]

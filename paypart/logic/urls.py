from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_payment_process, name='start_payment_process'),
    path('even_split/', views.even_split, name='even_split'),
    path('custom_split/', views.custom_split, name='custom_split'),
    path('holding_page', views.holding_page, name='holding_page'),
    path('success_page', views.success_page, name='success_page'),
    path('process_payments/', views.process_payments, name='process_payments'),

]

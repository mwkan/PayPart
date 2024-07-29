from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_payment_process, name='start_payment_process'),
    path('collect_user_amounts/', views.collect_user_amounts, name='collect_user_amounts'),
    # Add more paths for other views in your app here
]

from unicodedata import name
from django.urls import path
from . import views



urlpatterns=[
        path("",views.main, name="main"),
        path("main/",views.main, name="main"),
        
        path('verify_coin/',views.create_verify_page, name="create_verify_page"),
        path('verify_coin/get_verify/',views.get_verify, name="get_verify"),

        path('create_coin/', views.create_coin_page, name='create_coin_page'),
        path('create_coin/get_coin/', views.get_coin, name='get_coin'),

        path('sell_coin/', views.create_sell_page, name='create_sell_page'),
        path('sell_coin/get_sell/', views.get_sell, name='get_sell'),

        #path('divide_coin/', views.create_divide_page, name='create-divide_page'),
        #path('divide_coin/get_divide', views.divide_coin, name='divide_coin'),

        path('congregate_coin/', views.create_congregate_page, name='create_congregate_page'),
        path('congregate_coin/get_coin', views.congregate_coins, name='congregate_coin'),

        path('coins/', views.coin_list, name='coin_list'),

        #path('create_coin/create-payment/', views.create_payment, name='create_payment'),
        #path('webhook/', views.payment_webhook, name='payment_webhook'),
]
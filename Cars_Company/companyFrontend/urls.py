from django.urls import path
from . import views

app_name = "companyFrontend"

urlpatterns = [
    path('', views.loginPage, name='loginPage'),
    path('logout/', views.logout, name='logout'),
    path('index/', views.index, name='index'),
    path('cars/', views.cars, name='cars'),
    path('sold/', views.sold, name='sold'),
    path('manage/', views.manage, name='manage'),
    path('add_car/', views.add_car, name='add_car'),
    path('remove_car/', views.remove_car, name='remove_car'),
    path('sold_car/', views.sold_car, name='sold_car'),
    path('settings/', views.settings, name='settings'),
    path('add_admin/', views.add_admin, name='add_admin'),
    path('remove_admin/', views.remove_admin, name='remove_admin'),
    path('change_password/', views.change_password, name='change_password'),
    path('modify_car/', views.modify_car, name='modify_car'),
]
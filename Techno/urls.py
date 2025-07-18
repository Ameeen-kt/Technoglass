from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index , name='index'),
    path('home', home , name='home'),
    path('select_cust', select_cust , name='select_cust'),
    path('customer_register', customer_register , name='customer_register'),
    path('thickness_select', thickness_select , name='thickness_select'),
    path('measurements', measurements , name='measurements'),
    path('template_page', template_page , name='template_page'),
    path('extra_charges', extra_charges , name='extra_charges'),
    path('customer/profile/<int:customer_id>/', customer_profile_view, name='customer_profile_view'),
    path('customer/confirm/<int:customer_id>/', confirm_customer, name='confirm_customer'),
    path("save-and-print/", save_and_print, name="save_and_print"),
    path('summaries/', summary_list_view, name='summary_list'),
    path('template_page_edit/<int:summary_id>/', template_page_edit, name='template_page_edit'),
    path('summary/delete/<int:summary_id>/', delete_summary_view, name='delete_summary'),
    path('customers/', customer_list, name='customer_list'),
    path('edit_customer/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('delete_customer/<int:customer_id>/', delete_customer, name='delete_customer'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

]
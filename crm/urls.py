from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('export.xlsx', views.export_xlsx, name='export_xlsx'),

    path('clients/', views.clients_list, name='clients_list'),
    path('clients/new/', views.client_new, name='client_new'),
    path('clients/<str:client_id>/', views.client_detail, name='client_detail'),
    path('clients/<str:client_id>/edit/', views.client_edit, name='client_edit'),
    path('clients/<str:client_id>/delete/', views.client_delete, name='client_delete'),

    path('clients/<str:client_id>/contacts/new/', views.contact_new, name='contact_new'),
    path('contacts/<str:contact_id>/delete/', views.contact_delete, name='contact_delete'),

    path('clients/<str:client_id>/creds/new/', views.cred_new, name='cred_new'),
    path('creds/<str:cred_id>/delete/', views.cred_delete, name='cred_delete'),

    path('clients/<str:client_id>/links/new/', views.link_new, name='link_new'),
    path('links/<str:link_id>/delete/', views.link_delete, name='link_delete'),
]

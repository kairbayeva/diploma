from django.conf import settings # type: ignore
from django.conf.urls.static import static
from django.urls import path
from warehouse import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('forgot/', views.forgot_pw, name='forgot'),
    path('logout/', views.logout_page, name='logout'),
    path('index/', views.index, name='index'),
    path('manager_main/', views.manager_main, name='manager_main'),
    path('manager_product/<int:id>/', views.manager_product_page, name='manager_product_page'),
    path('products/', views.products, name='products_list'),
    path('product/<int:id>/', views.product_page, name='product_page'),
    path('providers_list/', views.providers_list, name='providers_list'),
    path('provider_page/<int:id>/', views.provider_page, name='provider_page'),
    path('recipient_list/', views.recipient_list, name='recipient_list'),
    path('recipient_page/<int:id>/', views.recipient_page, name='recipient_page'),
    path('inventory/', views.inventory, name='inventory'),
    path('shipment/', views.shipment, name='shipment'),
    path('coming/', views.coming, name='coming'),
    path('download_coming_report/', views.download_coming_report, name='download_coming_report'),
    path('download_shipment_report/', views.download_shipment_report, name='download_shipment_report'),
    path('download_inventory_report/', views.download_inventory_report, name='download_inventory_report'),
    path('download_material_report/', views.download_material_report, name='download_material_report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
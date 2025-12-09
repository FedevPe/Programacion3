"""
URL configuration for djangoPrueba project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('productos/', include("gestionProductos.urls")),
    path('proveedores/', include('gestionProveedores.urls')),
    path('clientes/', include("gestionClientes.urls")),
    path('ventas/', include("gestionVentas.urls")),
    path('', include("gestionUsuarios.urls")),
    path('compras/', include("gestionCompras.urls")),
    path('informes/', include('gestionInformes.urls')),



    path('stats/products/active/', views.count_active_products, name='stats_active_products'),
    path('stats/clients/active/', views.count_active_clients, name='stats_active_clients'),
    path('stats/providers/active/', views.count_active_providers, name='stats_active_providers'),
    path('stats/monthly-balance/', views.monthly_balance, name='stats_monthly_balance'),
    path('stats/home/', views.home_stats, name='stats_home_combined'),

]

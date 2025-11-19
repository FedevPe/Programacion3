from django.urls import path
from . import views

urlpatterns = [

    # PRODUCTOS
    path("productos/", views.productos_list, name="productos_list"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),
    path("productos/editar/<int:id>/", views.producto_editar, name="producto_editar"),
    path("productos/eliminar/<int:id>/", views.producto_eliminar, name="producto_eliminar"),

    # MARCAS
    path("marcas/", views.marcas_list, name="marcas_list"),
    path("marcas/crear/", views.marca_crear, name="marca_crear"),

    # CATEGORÍAS
    path("categorias/", views.categorias_list, name="categorias_list"),
    path("categorias/crear/", views.categoria_crear, name="categoria_crear"),
]

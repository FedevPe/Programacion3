from django.urls import path
from . import views

urlpatterns = [

    # MARCAS
    path("marcas/", views.marcas_list, name="marcas_list"),
    path("marcas/crear/", views.marca_crear, name="marca_crear"),
    path("marcas/editar/<int:id>/", views.marca_editar, name="marca_editar"),
    path("marcas/eliminar/<int:id>/", views.marca_eliminar, name="marca_eliminar"),

    # CATEGORÍAS
    path("categorias/", views.categorias_list, name="categorias_list"),
    path("categorias/crear/", views.categoria_crear, name="categoria_crear"),
    path("categorias/editar/<int:id>/", views.categoria_editar, name="categoria_editar"),
    path("categorias/eliminar/<int:id>/", views.categoria_eliminar, name="categoria_eliminar"),

    # PRODUCTOS
    path("productos/", views.productos_list, name="productos_list"),
    path("productos/detalle/<int:id>/", views.producto_detalle, name="producto_detalle"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),
    path("productos/editar/<int:id>/", views.producto_editar, name="producto_editar"),
    path("productos/eliminar/<int:id>/", views.producto_eliminar, name="producto_eliminar"),

    # MARCAS - AJAX
    path("marcas/ajax/crear/", views.marca_crear_ajax, name="marca_crear_ajax"),
    # CATEGORIAS - AJAX
    path("categorias/ajax/crear/", views.categoria_crear_ajax, name="categoria_crear_ajax"),
]


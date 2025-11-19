from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Productos, Marca, Categoria
from .forms import ProductoForm, MarcaForm, CategoriaForm

# ============================================================
# PRODUCTOS
# ============================================================
@login_required
def productos_list(request):
    productos = Productos.objects.all()
    return render(request, "productos/list.html", {"productos": productos})


@login_required
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado con éxito.")
            return redirect("productos_list")
    else:
        form = ProductoForm()

    return render(request, "productos/form.html", {"form": form})


@login_required
def producto_editar(request, id):
    producto = get_object_or_404(Productos, pk=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos_list")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "productos/form.html", {"form": form})


@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Productos, pk=id)
    producto.delete()
    messages.success(request, "Producto eliminado.")
    return redirect("productos_list")

# ============================================================
# MARCAS
# ============================================================
@login_required
def marcas_list(request):
    marcas = Marca.objects.all()
    return render(request, "marcas/list.html", {"marcas": marcas})


@login_required
def marca_crear(request):
    if request.method == "POST":
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca creada con éxito.")
            return redirect("marcas_list")
    else:
        form = MarcaForm()

    return render(request, "marcas/form.html", {"form": form})


# ============================================================
# CATEGORÍAS
# ============================================================
@login_required
def categorias_list(request):
    categorias = Categoria.objects.all()
    return render(request, "categorias/list.html", {"categorias": categorias})


@login_required
def categoria_crear(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada.")
            return redirect("categorias_list")
    else:
        form = CategoriaForm()

    return render(request, "categorias/form.html", {"form": form})

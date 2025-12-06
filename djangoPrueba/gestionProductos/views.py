from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Productos, Marca, Categoria
from .forms import ProductoForm, MarcaForm, CategoriaForm

# ============================================================
# PRODUCTOS
# ============================================================
@login_required
def productos_list(request):
    productos = Productos.objects.all()
    return render(request, "productos/productos_list.html", {"productos": productos})


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

    return render(request, "productos/productos_form.html", {"form": form})


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

    return render(request, "productos/productos_form.html", {"form": form})

@login_required
def producto_detalle(request, id):
    # Recupera el objeto Productos con el id proporcionado, o lanza un 404 si no existe.
    producto = get_object_or_404(Productos.objects.select_related('idMarca', 'idCategoria'), pk=id)    
    producto.precio_sin_iva = producto.precioUnitario / (1 + (producto.iva / 100))
    producto.precio_con_iva = producto.precioUnitario

    # Renderiza la plantilla de detalle, pasando el objeto producto.
    return render(request, "productos/productos_detalle.html", {"producto": producto})

@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Productos, pk=id)

    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("productos_list")

    # Si es GET: mostrar confirmación
    return render(request, "productos/productos_confirm_delete.html", {"producto": producto})

# ============================================================
# MARCAS
# ============================================================
@login_required
def marcas_list(request):
    marcas = Marca.objects.all()
    return render(request, "marcas/marcas_list.html", {"marcas": marcas})


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

    return render(request, "marcas/marcas_form.html", {"form": form})

def marca_editar(request, id):
    marca = get_object_or_404(Marca, pk=id)

    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca actualizada correctamente.")
            return redirect("marcas_list")
    else:
        form = MarcaForm(instance=marca)

    return render(request, "marcas/marcas_form.html", {"form": form, "accion": "Editar"})


@login_required
def marca_eliminar(request, id):
    marca = get_object_or_404(Marca, pk=id)

    if request.method == "POST":
        marca.delete()
        messages.success(request, f"Marca '{marca.nombre}' eliminada.")
        return redirect("marcas_list")

    return render(request, "marcas/marcas_confirm_delete.html", {"marca": marca})


# ============================================================
# CATEGORÍAS
# ============================================================
@login_required
def categorias_list(request):
    categorias = Categoria.objects.all()
    return render(request, "categorias/categorias_list.html", {"categorias": categorias})


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

    return render(request, "categorias/categorias_form.html", {"form": form})

@login_required
def categoria_editar(request, id):
    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect("categorias_list")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "categorias/categorias_form.html", {"form": form, "accion": "Editar"})

@login_required
def categoria_eliminar(request, id):
    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == "POST":
        nombre = categoria.descripcion
        categoria.delete()
        messages.success(request, f"Categoría '{nombre}' eliminada.")
        return redirect("categorias_list")

    return render(request, "categorias/categorias_confirm_delete.html", {"categoria": categoria})

@login_required
def marca_crear_ajax(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")

        if not nombre:
            return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

        marca = Marca.objects.create(nombre=nombre)

        return JsonResponse({
            "id": marca.idMarca,
            "nombre": marca.nombre
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def categoria_crear_ajax(request):
    if request.method == "POST":
        descripcion = request.POST.get("descripcion")

        if not descripcion:
            return JsonResponse({"error": "La descripción es obligatoria"}, status=400)

        categoria = Categoria.objects.create(descripcion=descripcion)

        return JsonResponse({
            "id": categoria.idCategoria,
            "descripcion": categoria.descripcion
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)
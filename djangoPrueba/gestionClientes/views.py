from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Cliente
from .forms import ClienteForm

# ============================================================
# CLIENTES
# ============================================================
@login_required
def clientes_list(request):
    """Lista todos los clientes"""
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    return render(request, "clientes/list.html", {"clientes": clientes})

@login_required
def cliente_detalle(request, id):
    """Muestra los datos de un cliente"""
    cliente = get_object_or_404(Cliente, idCliente=id)
    return render(request, "clientes/detalle.html", {"cliente": cliente})

@login_required
def cliente_crear(request):
    """Crea un nuevo cliente"""
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente creado con éxito.")
            return redirect("clientes_list")
    else:
        form = ClienteForm()

    return render(request, "clientes/form.html", {"form": form, "accion": "Crear"})


@login_required
def cliente_editar(request, id):
    """Edita un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=id)

    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("clientes_list")
    else:
        form = ClienteForm(instance=cliente)

    return render(request, "clientes/form.html", {"form": form, "accion": "Editar"})


# @login_required
# def cliente_eliminar(request, id):
#     """Elimina un cliente"""
#     cliente = get_object_or_404(Cliente, pk=id)
#     nombre_completo = cliente.nombre_completo()
#     cliente.delete()
#     messages.success(request, f"Cliente {nombre_completo} eliminado correctamente.")
#     return redirect("clientes_list")

@login_required
def cliente_confirmar_eliminar(request, id):
    """Muestra una pantalla de confirmación y elimina el cliente si se confirma."""
    cliente = get_object_or_404(Cliente, pk=id)

    if request.method == "POST":
        nombre_completo = cliente.nombre_completo()
        cliente.delete()
        messages.success(request, f"Cliente {nombre_completo} eliminado correctamente.")
        return redirect("clientes_list")

    # Si es GET, mostrar pantalla de confirmación
    return render(request, "clientes/confirmar_eliminar.html", {"cliente": cliente})

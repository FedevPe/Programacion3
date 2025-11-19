from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroUsuarioForm

# Create your views here.
# ============================================================
# LOGIN
# ============================================================
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect("home")
    else:
        form = LoginForm(request)

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ============================================================
# REGISTRO DE USUARIO
# ============================================================
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            user = usuario.user  # El campo OneToOneField
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            usuario.telefono = form.cleaned_data["telefono"]
            usuario.rol = form.cleaned_data["rol"]
            usuario.save()

            messages.success(request, "Usuario registrado correctamente.")
            return redirect("login")
    else:
        form = RegistroUsuarioForm()

    return render(request, "auth/registro.html", {"form": form})


# ============================================================
# HOME
# ============================================================
@login_required
def home(request):
    return render(request, "home.html")
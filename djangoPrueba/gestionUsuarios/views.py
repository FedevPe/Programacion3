from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm, RegistroUsuarioForm
from .models import Usuario

# ============================================================
# LOGIN
# ============================================================
def login_view(request):
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            
            # Redirigir a la página solicitada o al home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "auth/login.html", {"form": form})


# ============================================================
# LOGOUT
# ============================================================
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")


# # ============================================================
# # REGISTRO DE USUARIO
# # ============================================================
# def registro_usuario(request):
#     if request.method == "POST":
#         form = RegistroUsuarioForm(request.POST)
#         if form.is_valid():
#             try:
#                 # Crear el usuario de Django
#                 user = User.objects.create_user(
#                     username=form.cleaned_data['username'],
#                     email=form.cleaned_data['email'],
#                     first_name=form.cleaned_data['first_name'],
#                     last_name=form.cleaned_data['last_name'],
#                     password=form.cleaned_data['password1']
#                 )
                
#                 # Crear el perfil de Usuario
#                 usuario = Usuario.objects.create(
#                     user=user,
#                     telefono=form.cleaned_data.get('telefono', ''),
#                     rol=form.cleaned_data.get('rol')
#                 )
                
#                 messages.success(request, "Usuario registrado correctamente. Ya puedes iniciar sesión.")
#                 return redirect("login")
            
#             except Exception as e:
#                 messages.error(request, f"Error al registrar usuario: {str(e)}")
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{error}")
#     else:
#         form = RegistroUsuarioForm()

#     return render(request, "auth/registro.html", {"form": form})


# ============================================================
# HOME
# ============================================================
@login_required
def home(request):
    return render(request, "home.html")
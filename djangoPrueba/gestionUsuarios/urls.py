from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("registro/", views.registro_usuario, name="registro_usuario"),

    # HOME
    path("", views.home, name="home"),
]

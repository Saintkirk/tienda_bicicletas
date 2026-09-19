from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("bicicletas/", views.lista_bicicletas, name="lista_bicicletas"),
    path("bicicletas/crear/", views.crear_bicicleta, name="crear_bicicleta"),
    path("bicicletas/<int:pk>/editar/", views.editar_bicicleta, name="editar_bicicleta"),
    path("bicicletas/<int:pk>/eliminar/", views.eliminar_bicicleta, name="eliminar_bicicleta"),
]
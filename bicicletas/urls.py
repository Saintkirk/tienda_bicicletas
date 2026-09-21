from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path("", views.InicioView.as_view(), name="inicio"),
    path("bicicletas/", views.ListaBicicletasView.as_view(), name="lista_bicicletas"),
    
    # Ruta de creación de bicicleta corregida con el nombre 'crear_bicicleta'
    path("bicicletas/crear/", views.CrearBicicletaView.as_view(), name="crear_bicicleta"),
    
    path("bicicletas/<int:pk>/", views.DetalleBicicletaView.as_view(), name="detalle_bicicleta"),
    path("bicicletas/<int:pk>/editar/", views.EditarBicicletaView.as_view(), name="editar_bicicleta"),
    path("bicicletas/<int:pk>/eliminar/", views.EliminarBicicletaView.as_view(), name="bicicleta_eliminar"),
    
    # Rutas del carrito
    path("carrito/", views.CarritoView.as_view(), name="carrito"),
    path("carrito/agregar/<int:pk>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/eliminar/<int:pk>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/actualizar/<int:pk>/", views.actualizar_carrito, name="actualizar_carrito"),
    
    # Rutas de ventas
    path("ventas/", views.ListaVentasView.as_view(), name="lista_ventas"),
    path("ventas/crear/", views.CrearVentaView.as_view(), name="crear_venta"),
    path("ventas/<int:pk>/", views.DetalleVentaView.as_view(), name="detalle_venta"),
]
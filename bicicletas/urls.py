from django.urls import path
from . import views

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('lista/', views.ListaBicicletasView.as_view(), name='lista_bicicletas'),
    path('detalle/<int:pk>/', views.DetalleBicicletaView.as_view(), name='detalle_bicicleta'),
    path('crear/', views.CrearBicicletaView.as_view(), name='crear_bicicleta'),
    path('editar/<int:pk>/', views.EditarBicicletaView.as_view(), name='editar_bicicleta'),
    path('eliminar/<int:pk>/', views.EliminarBicicletaView.as_view(), name='eliminar_bicicleta'),
    
    # NUEVA RUTA: Eliminación múltiple
    path('eliminar-multiple/', views.eliminar_multiple_bicicletas, name='eliminar_multiple_bicicletas'),
    
    path('api/modelos-por-marca/', views.obtener_modelos_por_marca, name='obtener_modelos_por_marca'),

    # Carrito y Ventas
    path('carrito/', views.CarritoView.as_view(), name='carrito'),
    path('carrito/agregar/<int:pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:pk>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:pk>/', views.actualizar_carrito, name='actualizar_carrito'),
    
    path('venta/crear/', views.CrearVentaView.as_view(), name='crear_venta'),
    path('venta/detalle/<int:pk>/', views.DetalleVentaView.as_view(), name='detalle_venta'),
    path('ventas/', views.ListaVentasView.as_view(), name='lista_ventas'),
]
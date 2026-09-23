from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.ListaBicicletasView.as_view(), name='lista_bicicletas'),
    path('detalle/<int:pk>/', views.DetalleBicicletaView.as_view(), name='detalle_bicicleta'),
    path('crear/', views.CrearBicicletaView.as_view(), name='crear_bicicleta'),
    path('editar/<int:pk>/', views.EditarBicicletaView.as_view(), name='editar_bicicleta'),
    path('eliminar/<int:pk>/', views.EliminarBicicletaView.as_view(), name='eliminar_bicicleta'),
    
    # NUEVA RUTA: Eliminación múltiple
    path('eliminar-multiple/', views.eliminar_multiple_bicicletas, name='eliminar_multiple_bicicletas'),
    
    path('api/modelos-por-marca/', views.obtener_modelos_por_marca, name='obtener_modelos_por_marca'),

   
]
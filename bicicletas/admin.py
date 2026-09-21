from django.contrib import admin
from .models import Categoria, Marca, Modelo, Bicicleta, Cliente, Venta, ItemVenta, CarritoItem

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'segmento')

@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca')
    list_filter = ('marca',)

@admin.register(Bicicleta)
class BicicletaAdmin(admin.ModelAdmin):
    # Usamos 'modelo_rel' en lugar de 'marca' y 'modelo' antiguos
    list_display = ('id', 'modelo_rel', 'tipo', 'aro', 'precio', 'stock', 'estado', 'es_oferta')
    list_filter = ('tipo', 'estado', 'es_oferta', 'es_destacada')
    search_fields = ('modelo_rel__nombre', 'modelo_rel__marca__nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'estado', 'es_oferta')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'ciudad')
    search_fields = ('nombre', 'apellido', 'email')

class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_venta', 'total', 'metodo_pago')
    list_filter = ('metodo_pago', 'fecha_venta')
    inlines = [ItemVentaInline]

admin.site.register(CarritoItem)

from django.contrib import admin
from .models import Bicicleta

@admin.register(Bicicleta)
class BicicletaAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'tipo', 'aro', 'precio', 'stock')
    list_filter = ('tipo', 'marca')
    search_fields = ('marca', 'modelo')
# Register your models here.

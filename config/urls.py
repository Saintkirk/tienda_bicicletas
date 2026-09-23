from django.contrib import admin
from django.urls import include, path

# Eliminada la línea: from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluimos las URLs de la app bicicletas bajo el prefijo 'bicicletas/'
    path("bicicletas/", include("bicicletas.urls")),
    # Redirigimos la raíz principal también hacia las bicicletas
    path("", include("bicicletas.urls")),
]
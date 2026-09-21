from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluimos las URLs de la app bicicletas bajo el prefijo 'bicicletas/'
    path("bicicletas/", include("bicicletas.urls")),
    # Redirigimos la raíz principal también hacia las bicicletas (opcional pero muy útil)
    path("", include("bicicletas.urls")),
]
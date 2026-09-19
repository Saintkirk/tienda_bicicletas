from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Bicicleta(models.Model):
    TIPO_CHOICES = [
        ("MONTANA", "Montaña"),
        ("RUTA", "Ruta"),
        ("URBANA", "Urbana"),
        ("ELECTRICA", "Eléctrica"),
        ("INFANTIL", "Infantil"),
    ]

    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    aro = models.PositiveIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(29)]
    )
    precio = models.DecimalField(
        max_digits=10, decimal_places=0, validators=[MinValueValidator(1)]
    )
    stock = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Bicicleta"
        verbose_name_plural = "Bicicletas"

    def __str__(self):
        return f"{self.marca} {self.modelo}"
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


MAX_PRECIO_CLP = 99_999_999
TIPO_POR_CATEGORIA = {
    "Montaña": "MONTANA",
    "Ruta": "RUTA",
    "Urbana": "URBANA",
    "Eléctrica": "ELECTRICA",
    "Infantil": "INFANTIL",
}


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    segmento = models.CharField(max_length=50, default="MASIVA") # Ej: ALTA_GAMA, MASIVA, URBANA

    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    marca = models.ForeignKey(Marca, related_name="modelos", on_delete=models.CASCADE)
    categoria = models.ForeignKey(
        Categoria,
        related_name="modelos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"


class Bicicleta(models.Model):
    TIPO_CHOICES = [
        ("MONTANA", "Montaña"),
        ("RUTA", "Ruta"),
        ("URBANA", "Urbana"),
        ("ELECTRICA", "Eléctrica"),
        ("INFANTIL", "Infantil"),
    ]

    ESTADO_CHOICES = [
        ("DISPONIBLE", "Disponible"),
        ("AGOTADO", "Agotado"),
        ("RESERVADO", "Reservado"),
    ]

    # Relación directa con el modelo Modelo (que a su vez tiene la Marca)
    modelo_rel = models.ForeignKey(Modelo, on_delete=models.CASCADE, null=True, blank=True)
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    aro = models.PositiveIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(29)]
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_PRECIO_CLP)],
    )
    stock = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    categoria_rel = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="DISPONIBLE")
    stock_minimo = models.PositiveIntegerField(default=1)
    especificaciones = models.TextField(blank=True, null=True)
    es_oferta = models.BooleanField(default=False)
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_PRECIO_CLP)],
    )
    es_destacada = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Bicicleta"
        verbose_name_plural = "Bicicletas"

    def __str__(self):
        if self.modelo_rel:
            return f"{self.modelo_rel.marca.nombre} {self.modelo_rel.nombre}"
        return f"Bicicleta #{self.id}"

    def save(self, *args, **kwargs):
        if self.categoria_rel_id and self.categoria_rel:
            self.tipo = TIPO_POR_CATEGORIA.get(self.categoria_rel.nombre, self.tipo)
        super().save(*args, **kwargs)

    @property
    def marca(self):
        return self.modelo_rel.marca.nombre if self.modelo_rel else "Sin marca"

    @property
    def modelo(self):
        return self.modelo_rel.nombre if self.modelo_rel else "Sin modelo"

    @property
    def categoria(self):
        return self.categoria_rel.nombre if self.categoria_rel else "Sin categoría"




  


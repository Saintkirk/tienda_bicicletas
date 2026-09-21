from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
        max_digits=10, decimal_places=0, validators=[MinValueValidator(1)]
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
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    es_destacada = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Bicicleta"
        verbose_name_plural = "Bicicletas"

    def __str__(self):
        if self.modelo_rel:
            return f"{self.modelo_rel.marca.nombre} {self.modelo_rel.nombre}"
        return f"Bicicleta #{self.id}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ("EFECTIVO", "Efectivo"),
        ("TRANSFERENCIA", "Transferencia"),
        ("TARJETA", "Tarjeta de Crédito/Débito"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    metodo_pago = models.CharField(max_length=30, choices=METODO_PAGO_CHOICES, default="EFECTIVO")
    impuesto = models.DecimalField(max_digits=10, decimal_places=0, default=0, blank=True, null=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=0, default=0, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"


class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name="items", on_delete=models.CASCADE)
    bicicleta = models.ForeignKey(Bicicleta, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad}x {self.bicicleta} en Venta #{self.venta.id}"


class CarritoItem(models.Model):
    bicicleta = models.ForeignKey(Bicicleta, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    session_key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.cantidad} de {self.bicicleta}"
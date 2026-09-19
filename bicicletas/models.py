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

    MARCA_CHOICES = [
        (
            "Alta Gama e Internacionales",
            [
                ("TREK", "Trek"),
                ("SPECIALIZED", "Specialized"),
                ("GIANT", "Giant"),
                ("SCOTT", "Scott"),
                ("CANNONDALE", "Cannondale"),
                ("ORBEA", "Orbea"),
                ("PINARELLO", "Pinarello"),
                ("BIANCHI", "Bianchi"),
                ("CERVELO", "Cervélo"),
                ("BMC", "BMC Switzerland"),
                ("SANTA_CRuz", "Santa Cruz"),
                ("YETI", "Yeti Cycles"),
                ("GT", "GT Bicycles"),
                ("MERIDA", "Merida"),
                ("KTM", "KTM Bikes"),
                ("CUBE", "Cube Bikes"),
                ("FOCUS", "Focus Bikes"),
                ("WILIER", "Wilier Triestina"),
                ("COLNAGO", "Colnago"),
                ("DE_ROSA", "De Rosa"),
                ("RIDLEY", "Ridley"),
                ("LOOK", "Look Cycle"),
                ("TIME", "Time Sport"),
                ("FACTOR", "Factor Bikes"),
                ("ARGON_18", "Argon 18"),
                ("LAPIERRE", "Lapierre"),
                ("COMMENCAL", "Commencal"),
                ("TRANSITION", "Transition Bikes"),
                ("NORCO", "Norco"),
                ("KONA", "Kona"),
                ("ROCKY_MOUNTAIN", "Rocky Mountain"),
                ("INTENSE", "Intense Cycles"),
                ("EVIL", "Evil Bikes"),
                ("IBIS", "Ibis Cycles"),
                ("PIVOT", "Pivot Cycles"),
                ("MACEK", "Macek"),
                ("BANSHEE", "Banshee Bikes"),
                ("NS_BIKES", "NS Bikes"),
                ("DARTMOOR", "Dartmoor"),
                ("STUMPJUMPER", "Stumpjumper"),
            ],
        ),
        (
            "Masivas y Populares en Chile",
            [
                ("OXFORD", "Oxford"),
                ("UPLAND", "Upland"),
                ("LEADER", "Leader"),
                ("PRO_MAX", "Pro Max"),
                ("AVANT", "Avant"),
                ("ROBUSTA", "Robusta"),
                ("KRONOS", "Kronos"),
                ("WINDSOR", "Windsor"),
                ("BENOTTO", "Benotto"),
                ("MONGOOSE", "Mongoose"),
                ("SCHWINN", "Schwinn"),
                ("HARO", "Haro Bikes"),
                ("DIAMONDBACK", "Diamondback"),
                ("RALEIGH", "Raleigh"),
                ("HASA", "Hasa"),
                ("TRINX", "Trinx"),
                ("JAVA", "Java Bikes"),
                ("SAVA", "Sava"),
                ("TWITTER", "Twitter Bikes"),
                ("AUDACIOUS", "Audacious"),
                ("MOOSE", "Moose"),
                ("CANNON", "Cannon"),
                ("STARK", "Stark"),
                ("MOSSO", "Mosso"),
                ("SHOGUN", "Shogun"),
                ("KENSLER", "Kensler"),
                ("ECLIPSE", "Eclipse"),
                ("FROST", "Frost"),
            ],
        ),
        (
            "Urbanas, Plegables y Eléctricas",
            [
                ("DECATHLON", "Decathlon / B'Twin"),
                ("ELECTRA", "Electra"),
                ("BROOKLYN", "Brooklyn Bicycle Co."),
                ("STRIDA", "Strida"),
                ("BROMPTON", "Brompton"),
                ("TERN", "Tern"),
                ("DAHON", "Dahon"),
                ("GAZELLE", "Gazelle"),
                ("RAD_POWER", "Rad Power Bikes"),
                ("HAIBIKE", "Haibike"),
                ("SPECIALIZED_E", "Specialized Turbo"),
                ("BULLS", "Bulls Bikes"),
            ],
        ),
        (
            "BMX y Freestyle",
            [
                ("PRIMO", "Primo"),
                ("SUBROSA", "Subrosa"),
                ("WETHEPEOPLE", "WeThePeople"),
                ("DIAMOND", "Diamond"),
                ("BSD", "BSD"),
                ("ODYSSEY", "Odyssey"),
                ("CULT", "Cult Crew"),
                ("STOLEN", "Stolen Bikes"),
                ("SE_BIKES", "SE Bikes"),
                ("FIT_BIKE_CO", "Fit Bike Co."),
            ],
        ),
        (
            "Otras",
            [
                ("OTRA", "Otra / Genérica"),
            ],
        ),
    ]

    marca = models.CharField(max_length=40, choices=MARCA_CHOICES)
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
        return f"{self.get_marca_display()} {self.modelo}"
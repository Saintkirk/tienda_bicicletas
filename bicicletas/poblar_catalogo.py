import os
import sys
import django
import random

current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bicicletas.models import Categoria, Marca, Modelo

print("--- Iniciando carga avanzada con Precios Chile y Colores ---")

# 1. Crear Categorías Base
categorias_data = {
    "Montaña": "Bicicletas para senderos y terrenos irregulares (MTB).",
    "Ruta": "Bicicletas livianas para pavimento y carretera.",
    "Urbana": "Bicicletas para transporte y movilidad urbana.",
    "Eléctrica": "Bicicletas con asistencia eléctrica (E-Bike).",
    "Infantil": "Bicicletas para niños y niñas.",
    "Plegable": "Bicicletas diseñadas para plegarse y facilitar transporte.",
    "Gravel": "Bicicletas versátiles para mixto (tierra y asfalto).",
}

for nombre, desc in categorias_data.items():
    Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc, "activa": True})

# 2. Paletas de colores asociadas según gama o estilo
PALETAS_COLORES = {
    "ALTA_GAMA": ["Negro Mate", "Carbono Brillo", "Azul Perla", "Rojo Competencia", "Plomo Titanio"],
    "MASIVA": ["Negro/Rojo", "Azul Acero", "Verde Militar", "Blanco Perla", "Gris Grafito"],
    "ENTRADA": ["Rojo Brillante", "Celeste Pastel", "Amarillo Flúor", "Rosado", "Negro"],
    "LICENCIA": ["Negro Elegante", "Plomo Plata", "Blanco Glaciar"]
}

def obtener_categoria(marca, modelo):
    texto = f"{marca} {modelo}".lower()
    if any(k in texto for k in ["electric", "e-bike", "e-", "turbo", "gain", "ter", "vant", "neo", "axis", "ion", "bat", "motor"]):
        return "Eléctrica"
    if any(k in texto for k in ["kid", "junior", "infantil", "balance", "boys", "girls", "niño", "niña"]):
        return "Infantil"
    if any(k in texto for k in ["fold", "pleg", "tilt", "brompton", "dahon"]):
        return "Plegable"
    if any(k in texto for k in ["domane", "emonda", "tarmac", "roubaix", "defy", "propel", "addict", "synapse", "caad", "alez", "via nirone", "sprint", "impulso", "contend", "fastroad", "escape"]):
        return "Ruta"
    if any(k in texto for k in ["checkpoint", "topstone", "jari", "revolt", "warbird", "allcity", "canyon grizl"]):
        return "Gravel"
    if any(k in texto for k in ["city", "urban", "riverside", "dew", "fairfax", "kentfield", "traffic", "brisa", "voyage", "life", "street"]):
        return "Urbana"
    return "Montaña"

def estimar_precio_chile(marca, categoria, modelo_texto):
    """Estima un precio razonable en pesos chilenos (CLP) según el segmento."""
    texto = modelo_texto.lower()
    
    # Si es eléctrica, el valor base es alto en Chile
    if categoria == "Eléctrica" or "turbo" in texto or "powerfly" in texto:
        return random.randint(1800000, 4500000)
    
    # Marcas de alta gama
    if marca in ["Trek", "Specialized", "Giant", "Scott", "Cannondale", "Bianchi", "Brompton"]:
        if "s-works" in texto or "scalpel" in texto or "supercaliber" in texto:
            return random.randint(3500000, 6500000)
        return random.randint(850000, 2400000)
    
    # Marcas masivas / nacionales (Oxford, Upland, Lahsen, etc.)
    if categoria == "Infantil":
        return random.randint(90000, 180000)
    if categoria == "Plegable":
        return random.randint(250000, 600000)
    
    return random.randint(190000, 550000)

# Catálogo completo unificado
catalogo_general = {
    "Oxford": [
        ("Mito 1", 26), ("Mito 5", 29), ("Merak 3", 29), ("Orion 3", 27), 
        ("Terra 5", 29), ("Brisa", 26), ("Volcano", 29)
    ],
    "Trek": [
        ("Marlin 5", 29), ("Marlin 7", 29), ("Marlin 8", 29),
        ("Domane AL 2", 28), ("Checkpoint ALR", 28), ("Powerfly 4", 29)
    ],
    "Specialized": [
        ("Rockhopper Sport", 29), ("Chisel", 29),
        ("Allez", 28), ("Roubaix", 28), ("Turbo Levo", 29)
    ],
    "Giant": [
        ("Talon 1", 29), ("Anthem", 29), ("Defy", 28), ("Stance E+", 29)
    ],
    "Cannondale": [
        ("Trail 3", 29), ("Scalpel", 29), ("Topstone", 28)
    ],
    "Bianchi": [
        ("Magma 9.1", 29), ("Via Nirone 7", 28), ("E-Omnia", 28)
    ],
    "Brompton": [
        ("C Line Explore", 16), ("Electric C Line", 16)
    ]
}

contador_marcas = 0
contador_modelos = 0

for nombre_marca, lista_modelos in catalogo_general.items():
    segmento = "MASIVA"
    if nombre_marca in ["Trek", "Specialized", "Giant", "Scott", "Cannondale", "Bianchi", "Brompton"]:
        segmento = "ALTA_GAMA"
    elif nombre_marca in ["Decathlon / B'Twin", "Aro 29"]:
        segmento = "ENTRADA"
    elif nombre_marca in ["BMW", "Jeep"]:
        segmento = "LICENCIA"

    marca_obj, created = Marca.objects.update_or_create(
        nombre=nombre_marca,
        defaults={"segmento": segmento}
    )
    if created: contador_marcas += 1

    for nombre_modelo_base, aro in lista_modelos:
        nombre_completo = f"{nombre_modelo_base} (Aro {aro})"
        cat_nombre = obtener_categoria(nombre_marca, nombre_modelo_base)
        
        try:
            categoria_obj = Categoria.objects.get(nombre=cat_nombre)
        except Categoria.DoesNotExist:
            categoria_obj = Categoria.objects.first()

        # Precio estimado para referencia en CLP
        precio_sugerido = estimar_precio_chile(nombre_marca, cat_nombre, nombre_modelo_base)

        modelo_obj, created = Modelo.objects.update_or_create(
            marca=marca_obj,
            nombre=nombre_completo,
            defaults={"categoria": categoria_obj}
        )
        if created: 
            contador_modelos += 1

print(f"\n¡Carga finalizada con éxito!")
print(f"- Marcas totales: {Marca.objects.count()}")
print(f"- Modelos totales: {Modelo.objects.count()}")
print("Se han asignado categorías inteligentes y parámetros base para el mercado chileno.")
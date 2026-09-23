import os
import sys
import django

# Agrega la ruta raíz del proyecto al sistema
current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(current_path)

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bicicletas.models import Categoria, Marca, Modelo

print("--- Iniciando carga de catálogo Chile ---")

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

def obtener_categoria(marca, modelo):
    """Determina la categoría basándose en palabras clave del nombre."""
    texto = f"{marca} {modelo}".lower()
    
    # Prioridad 1: Eléctricas
    if any(k in texto for k in ["electric", "e-bike", "e-", "turbo", "gain", "ter", "vant", "neo", "axis", "ion", "bat", "motor"]):
        return "Eléctrica"
    
    # Prioridad 2: Infantiles
    if any(k in texto for k in ["kid", "junior", "infantil", "balance", "boys", "girls", "niño", "niña"]):
        return "Infantil"
        
    # Prioridad 3: Plegables
    if any(k in texto for k in ["fold", "pleg", "tilt", "brompton", "dahon"]):
        return "Plegable"

    # Prioridad 4: Ruta / Carretera
    if any(k in texto for k in ["domane", "emonda", "tarmac", "roubaix", "defy", "propel", "addict", "synapse", "caad", "alez", "via nirone", "sprint", "impulso", "contend", "fastroad", "escape"]):
        return "Ruta"
        
    # Prioridad 5: Gravel
    if any(k in texto for k in ["checkpoint", "topstone", "jari", "revolt", "warbird", "allcity", "canyon grizl"]):
        return "Gravel"

    # Prioridad 6: Urbanas / Paseo
    if any(k in texto for k in ["city", "urban", "riverside", "dew", "fairfax", "kentfield", "traffic", "brisa", "voyage", "life", "street"]):
        return "Urbana"

    # Default: Montaña (la mayoría de los modelos sin etiqueta específica suelen ser MTB en este contexto)
    return "Montaña"

# 2. Catálogo General (MTB, Ruta, Urbano)
catalogo_general = {
    "Oxford": [
        ("Mito 1", 26), ("Mito 3", 27), ("Mito 5", 29),
        ("Merak 1", 27), ("Merak 2", 29), ("Merak 3", 29), ("Merak 7", 29),
        ("Orion 1", 26), ("Orion 3", 27), ("Orion 5", 29), ("Orion 7", 29),
        ("Terra 1", 27), ("Terra 2", 29), ("Terra 5", 29),
        ("Brisa", 26), ("Konna", 27), ("Largo", 29), ("Rider", 26),
        ("Volcano", 29), ("Andes", 29), ("Patagonia", 29)
    ],
    "Upland": [
        ("Vanguard 100", 26), ("Vanguard 200", 27), ("Vanguard 300", 29), ("Vanguard 500", 29),
        ("Lander 100", 27), ("Lander 300", 29), ("Lander 500", 29),
        ("X-Trail 200", 27), ("X-Trail 500", 29), ("Sentinel", 29),
        ("Mobius", 29), ("Sorento", 29)
    ],
    "Aro 29": [
        ("Speed", 29), ("Track", 29), ("X-Treme", 29), ("Fire", 29),
        ("Urban", 28), ("City", 28), ("Junior", 24)
    ],
    "Megamo": [
        ("Freedom", 29), ("Spirit", 29), ("Hunter", 29), ("Slayer", 29),
        ("Road", 28), ("Fit", 28)
    ],
    "Phoenix": [
        ("Expert", 29), ("Pro", 29), ("Master", 27), ("Grand", 29),
        ("Urban Life", 28), ("Fold", 20)
    ],
    "Trek": [
        ("Marlin 4", 27), ("Marlin 4", 29), ("Marlin 5", 27), ("Marlin 5", 29),
        ("Marlin 6", 29), ("Marlin 7", 29), ("Marlin 8", 29),
        ("X-Caliber 7", 29), ("X-Caliber 8", 29), ("X-Caliber 9", 29),
        ("Supercaliber", 29), ("Procaliber", 29), ("Top Fuel", 29),
        ("Domane AL 2", 28), ("Domane AL 4", 28), ("Checkpoint ALR", 28), ("Emonda SL", 28)
    ],
    "Specialized": [
        ("Rockhopper Sport", 27), ("Rockhopper Sport", 29), ("Rockhopper Comp", 29),
        ("Chisel", 29), ("Stumpjumper", 29), ("Epic Hardtail", 29),
        ("Allez", 28), ("Allez Sport", 28), ("Roubaix", 28), ("Tarmac", 28),
        ("Turbo Levo", 29), ("Turbo Tero", 29) # Estos se marcarán como eléctricos por la lógica
    ],
    "Giant": [
        ("Talon 0", 27), ("Talon 0", 29), ("Talon 1", 29), ("Talon 2", 29), ("Talon 3", 27), ("Talon 4", 26),
        ("Anthem", 29), ("Trance", 29), ("Reign", 29),
        ("Fathom", 29), ("Stance", 29),
        ("Defy", 28), ("Contend", 28), ("Propel", 28), ("Fastroad", 28)
    ],
    "Leader": [
        ("Fox", 26), ("Fox", 27), ("Catfish", 24), ("Viper", 26), 
        ("Agressor", 27), ("Vector", 29), ("Spider", 26), ("Raptor", 29)
    ],
    "Scott": [
        ("Scale 960", 29), ("Scale 970", 29), ("Scale 980", 29),
        ("Aspect 740", 27), ("Aspect 760", 27), ("Aspect 930", 29),
        ("Addict", 28), ("Speedster", 28), ("Genius", 29), ("Strike", 29)
    ],
    "Cannondale": [
        ("Trail 1", 29), ("Trail 3", 29), ("Trail 5", 27), ("Trail 7", 26),
        ("Scalpel", 29), ("Habit", 29),
        ("Synapse", 28), ("CAAD Optimo", 28), ("Topstone", 28)
    ],
    "Bianchi": [
        ("Magma 7.0", 27), ("Magma 9.1", 29), ("JAB", 29),
        ("Via Nirone 7", 28), ("Sprint", 28), ("Impulso", 28), ("Nirone 7", 28)
    ],
    "Decathlon / B'Twin": [
        ("Rockrider ST 100", 27), ("Rockrider ST 120", 27), ("Rockrider ST 530", 27), ("Rockrider ST 530", 29),
        ("Rockrider XC 100", 29), ("Rockrider XC 500", 29),
        ("Riverside 100", 28), ("Riverside 120", 28), ("Riverside 500", 28),
        ("Tilt 100", 20), ("Tilt 500", 20)
    ],
    "BMW": [
        ("Bike Cruise", 28), ("Bike Attiv", 28), ("Bike Air", 29), ("BMWi", 28)
    ],
    "Jeep": [
        ("Wrangler", 29), ("Renegade", 29), ("Compass", 29), ("Grand Cherokee", 29)
    ],
    "Masisa": [
        ("Thunder", 29), ("Storm", 29), ("Cloud", 28), ("Rain", 27)
    ],
    "Trinx": [
        ("M100", 26), ("M120", 27), ("M130", 29), ("K200", 29), ("X3", 29)
    ],
    "Monark": [
        ("Mountain", 26), ("Mountain", 29), ("Urban", 28), ("Junior", 20)
    ],
    "Caloi": [
        ("Explorer", 29), ("Sport", 29), ("Urban", 28), ("Elite", 28)
    ],
    "Venzo": [
        ("Raptor", 29), ("Skyline", 29), ("Primal", 27), ("Flex", 28), ("Eolo", 28)
    ],
    "Lahsen": [
        ("Mountain Pro", 29), ("Montana", 27), ("City", 28), ("Junior", 24)
    ],
    "Brompton": [
        ("C Line Explore", 16), ("C Line Urban", 16), ("P Line", 16), ("Electric C Line", 16)
    ]
}

# 3. Catálogo Específico de Eléctricas (Para asegurar que existan estos modelos)
# Aunque la lógica automática las detecta, es bueno tenerlas explícitas si el nombre no es obvio
catalogo_electricos = {
    "Trek": [
        ("Powerfly 4", 29), ("Powerfly 5", 29), ("Powerfly 7", 29),
        ("Allant+ 5", 28), ("Allant+ 7", 28), ("Allant+ 9", 28),
        ("Rail 5", 29), ("Rail 7", 29)
    ],
    "Specialized": [
        ("Turbo Levo SL", 29), ("Turbo Levo Comp", 29), ("Turbo Kenevo", 29),
        ("Turbo Vado 3.0", 28), ("Turbo Vado 4.0", 28), ("Turbo Como 3.0", 28),
        ("Turbo Creo SL", 28)
    ],
    "Giant": [
        ("Explore E+", 28), ("Escape E+", 28), ("Road E+", 28),
        ("Stance E+", 29), ("Trance X E+", 29), ("Reign E+", 29),
        ("FastRoad E+", 28), ("Delite E+", 28)
    ],
    "Oxford": [
        ("E-Merak", 29), ("E-Terra", 29), ("E-Volcano", 29), ("E-City", 28)
    ],
    "Upland": [
        ("E-Vanguard", 29), ("E-Lander", 29), ("E-Mobius", 29)
    ],
    "Scott": [
        ("Strike eRIDE", 29), ("Genius eRIDE", 29), ("Axis eRIDE", 28), ("Sub Cross eRIDE", 28)
    ],
    "Cannondale": [
        ("Moterra", 29), ("Habit NEO", 29), ("Quick NEO", 28), ("Synapse NEO", 28)
    ],
    "Bianchi": [
        ("T-Tronik", 29), ("E-Suvanto", 28), ("E-Omnia", 28)
    ],
    "Cube": [
        ("Reaction Hybrid", 29), ("Stereo Hybrid", 29), ("Kathmandu Hybrid", 28), ("Travel Hybrid", 28)
    ],
    "Haibike": [
        ("SDURO HardSeven", 29), ("SDURO FullSeven", 29), ("XDURO AllMtn", 29), ("XDURO Trekking", 28)
    ],
    "Riese & Müller": [
        ("Nevo4", 28), ("Supercharger4", 29), ("Delite4", 29), ("Packster4", 26) # Cargo
    ],
    "Stromer": [
        ("ST5", 28), ("SP5", 28), ("X5", 28)
    ]
}

# Unir catálogos para procesamiento
todos_los_datos = {**catalogo_general, **catalogo_electricos}

contador_marcas = 0
contador_modelos = 0

for nombre_marca, lista_modelos in todos_los_datos.items():
    # Determinar segmento de mercado
    segmento = "MASIVA"
    if nombre_marca in ["Trek", "Specialized", "Giant", "Scott", "Cannondale", "Bianchi", "Riese & Müller", "Haibike"]:
        segmento = "ALTA_GAMA"
    elif nombre_marca in ["Decathlon / B'Twin", "Aro 29", "Phoenix"]:
        segmento = "ENTRADA"
    elif nombre_marca in ["BMW", "Jeep"]:
        segmento = "LICENCIA"

    # Crear o obtener Marca
    marca_obj, created = Marca.objects.update_or_create(
        nombre=nombre_marca,
        defaults={"segmento": segmento}
    )
    if created: contador_marcas += 1

    # Procesar Modelos
    for nombre_modelo_base, aro in lista_modelos:
        # Formatear nombre completo
        nombre_completo = f"{nombre_modelo_base} (Aro {aro})"
        
        # Obtener categoría dinámica
        cat_nombre = obtener_categoria(nombre_marca, nombre_modelo_base)
        try:
            categoria_obj = Categoria.objects.get(nombre=cat_nombre)
        except Categoria.DoesNotExist:
            categoria_obj = Categoria.objects.first() # Fallback

        # Crear o actualizar Modelo
        modelo_obj, created = Modelo.objects.update_or_create(
            marca=marca_obj,
            nombre=nombre_completo,
            defaults={"categoria": categoria_obj}
        )
        if created: 
            contador_modelos += 1
            # print(f"  + Agregado: {nombre_marca} - {nombre_completo} [{cat_nombre}]")

print(f"\n¡Proceso terminado!")
print(f"- Marcas verificadas/creadas: {contador_marcas} nuevas (Total en DB: {Marca.objects.count()})")
print(f"- Modelos verificados/creados: {contador_modelos} nuevos (Total en DB: {Modelo.objects.count()})")
print("- Las categorías se asignaron automáticamente según el nombre del modelo.")
print("¡Ya puedes crear bicicletas con datos reales del mercado chileno!")
import os
import sys
import django

# Agrega la ruta raíz del proyecto al sistema para que reconozca 'config'
current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_path)

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bicicletas.models import Marca, Modelo

# Catálogo estructurado con marcas y sus modelos (con aros enteros)
catalogo_con_aros = {
    "Trek": [
        ("Marlin 4", 27), ("Marlin 4", 29),
        ("Marlin 5", 27), ("Marlin 5", 29),
        ("Marlin 6", 29), ("Marlin 7", 29), ("Marlin 8", 29),
        ("X-Caliber 7", 29), ("X-Caliber 8", 29), ("X-Caliber 9", 29),
        ("Supercaliber", 29), ("Procaliber 9.5", 29), ("Top Fuel", 29),
        ("Domane AL 2", 28), ("Domane AL 4", 28), ("Checkpoint ALR 5", 28), ("Emonda SL 5", 28)
    ],
    "Specialized": [
        ("Rockhopper Sport", 27), ("Rockhopper Sport", 29),
        ("Rockhopper Comp", 29), ("Rockhopper Expert", 29),
        ("Chisel", 29), ("Stumpjumper Alloy", 29), ("Stumpjumper Expert", 29),
        ("Epic Hardtail", 29), ("Epic Evo", 29),
        ("Allez", 28), ("Allez Sport", 28), ("Roubaix", 28), ("Tarmac SL7", 28),
        ("Turbo Levo", 29), ("Turbo Tero", 29)
    ],
    "Giant": [
        ("Talon 0", 27), ("Talon 0", 29),
        ("Talon 1", 29), ("Talon 2", 29), ("Talon 3", 27), ("Talon 3", 29), ("Talon 4", 26),
        ("Anthem Advanced", 29), ("Trance X", 29), ("Reign 29", 29),
        ("Fathom 2", 29), ("Stance 29", 29),
        ("Defy Advanced", 28), ("Contend 1", 28), ("Contend 2", 28), ("Propel Advanced", 28)
    ],
    "Oxford": [
        ("Mito 1", 26), ("Mito 3", 27), ("Mito 5", 29),
        ("Merak 1", 27), ("Merak 2", 29), ("Merak 3", 29),
        ("Orion 1", 26), ("Orion 3", 27), ("Orion 5", 29),
        ("Terra 1", 27), ("Terra 2", 29),
        ("Brisa", 26), ("Konna", 27), ("Largo", 29), ("Rider", 26)
    ],
    "Upland": [
        ("Vanguard 100", 26), ("Vanguard 200", 27), ("Vanguard 300", 29),
        ("Lander 100", 27), ("Lander 300", 29),
        ("X-Trail 200", 27), ("X-Trail 500", 29), ("Sentinel", 29)
    ],
    "Leader": [
        ("Fox", 26), ("Fox", 27), ("Catfish", 24), ("Viper", 26), ("Agressor", 27), ("Vector", 29), ("Spider", 26)
    ],
    "Scott": [
        ("Scale 960", 29), ("Scale 970", 29), ("Scale 980", 29),
        ("Aspect 740", 27), ("Aspect 760", 27), ("Aspect 930", 29),
        ("Addict RC 40", 28), ("Speedster 40", 28), ("Genius 940", 29)
    ],
    "Cannondale": [
        ("Trail 1", 29), ("Trail 3", 29), ("Trail 5", 27), ("Trail 5", 29), ("Trail 7", 26),
        ("Scalpel HT", 29), ("Habit", 29),
        ("Synapse", 28), ("CAAD Optimo", 28), ("Topstone 4", 28)
    ],
    "Bianchi": [
        ("Magma 7.0", 27), ("Magma 9.1", 29), ("JAB", 29),
        ("Via Nirone 7", 28), ("Sprint", 28), ("Impulso", 28)
    ],
    "Decathlon / B'Twin": [
        ("Rockrider ST 100", 27), ("Rockrider ST 120", 27), ("Rockrider ST 530", 27), ("Rockrider ST 530", 29),
        ("Riverside 100", 28), ("Riverside 120", 28),
        ("Tilt 100", 20), ("Tilt 500", 20)
    ]
}

# Poblar las tablas Marca y Modelo
for nombre_marca, lista_datos in catalogo_con_aros.items():
    segmento = "MASIVA"
    if nombre_marca in ["Trek", "Specialized", "Giant", "Scott", "Cannondale", "Bianchi"]:
        segmento = "ALTA_GAMA"
    elif nombre_marca in ["Decathlon / B'Twin"]:
        segmento = "URBANA"

    marca_obj, _ = Marca.objects.get_or_create(
        nombre=nombre_marca, 
        defaults={"segmento": segmento}
    )
    
    for nombre_modelo, aro in lista_datos:
        nombre_con_aro = f"{nombre_modelo} (Aro {aro})"
        Modelo.objects.get_or_create(
            marca=marca_obj, 
            nombre=nombre_con_aro
        )

print("¡Catálogo de Marcas y Modelos integrado correctamente en la base de datos!")
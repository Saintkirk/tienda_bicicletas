from django.db import migrations, models
import django.db.models.deletion


def clasificar_modelos(apps, schema_editor):
    Categoria = apps.get_model("bicicletas", "Categoria")
    Modelo = apps.get_model("bicicletas", "Modelo")
    categorias = {
        "Montaña": "Bicicletas para senderos y terrenos irregulares.",
        "Ruta": "Bicicletas livianas para pavimento y carretera.",
        "Urbana": "Bicicletas para transporte y movilidad urbana.",
        "Eléctrica": "Bicicletas con asistencia eléctrica.",
        "Infantil": "Bicicletas para niños y niñas.",
    }
    categoria_objetos = {}
    for nombre, descripcion in categorias.items():
        categoria_objetos[nombre], _ = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={"descripcion": descripcion, "activa": True},
        )

    for modelo in Modelo.objects.select_related("marca").all():
        nombre = f"{modelo.marca.nombre} {modelo.nombre}".lower()
        if any(palabra in nombre for palabra in ("kid", "junior", "infantil", "balance")):
            categoria = "Infantil"
        elif any(palabra in nombre for palabra in ("electric", "e-bike", "e-", "turbo", "gain")):
            categoria = "Eléctrica"
        elif any(palabra in nombre for palabra in ("domane", "checkpoint", "emonda", "via nirone", "allez", "roubaix", "tarmac", "defy", "contend", "propel", "addict", "speedster", "synapse", "caad", "topstone", "jari")):
            categoria = "Ruta"
        elif any(palabra in nombre for palabra in ("city", "urban", "riverside", "tilt", "dew", "fairfax", "kentfield", "traffic", "brisa")):
            categoria = "Urbana"
        else:
            categoria = "Montaña"
        modelo.categoria_id = categoria_objetos[categoria].id
        modelo.save(update_fields=["categoria"])


class Migration(migrations.Migration):

    dependencies = [
        ("bicicletas", "0007_limite_precios_bicicleta"),
    ]

    operations = [
        migrations.AddField(
            model_name="modelo",
            name="categoria",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="modelos",
                to="bicicletas.categoria",
            ),
        ),
        migrations.RunPython(clasificar_modelos, migrations.RunPython.noop),
    ]
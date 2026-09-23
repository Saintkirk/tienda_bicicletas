from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("bicicletas", "0006_marca_remove_bicicleta_categoria_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bicicleta",
            name="precio",
            field=models.DecimalField(
                decimal_places=0,
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(99999999),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="bicicleta",
            name="precio_oferta",
            field=models.DecimalField(
                blank=True,
                decimal_places=0,
                max_digits=10,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(99999999),
                ],
            ),
        ),
    ]

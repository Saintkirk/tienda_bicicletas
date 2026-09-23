from django import forms
from .models import (
    Bicicleta,
    Categoria,
    Marca,
    Modelo,
)
import json

# Definimos el límite máximo comercial para Chile (10 millones de pesos)
MAX_PRECIO_CLP = 10000000


class ModeloSelect(forms.Select):
    """
    Widget personalizado para el campo Modelo.
    Inyecta atributos data-categoria y data-aros en cada <option>
    para permitir el filtrado dinámico en el frontend.
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        if value and hasattr(value, "instance"):
            instancia = value.instance if hasattr(value, 'instance') else value
            
            if instancia.categoria_id:
                option["attrs"]["data-categoria"] = str(instancia.categoria_id)
            
            aros_validos = []
            if "(Aro" in instancia.nombre:
                try:
                    aro_str = instancia.nombre.split("(Aro")[-1].split(")")[0].strip()
                    if aro_str.isdigit():
                        aros_validos = [int(aro_str)]
                except:
                    pass
            
            if aros_validos:
                option["attrs"]["data-aros"] = json.dumps(aros_validos)
        
        return option


class BicicletaForm(forms.ModelForm):
    """Formulario para gestión de bicicletas con filtrado dinámico"""

    marca = forms.ModelChoiceField(
        queryset=Marca.objects.order_by("nombre"),
        empty_label="Seleccione una marca",
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_marca"}),
    )
    
    modelo_rel = forms.ModelChoiceField(
        queryset=Modelo.objects.none(),
        empty_label="Seleccione primero una marca",
        required=True,
        widget=ModeloSelect(attrs={"class": "form-select", "id": "id_modelo_rel"}),
    )

    categoria_rel = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True).order_by("nombre"),
        empty_label="Seleccione un modelo para ver la categoría",
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_categoria_rel", "disabled": True}),
    )

    aro = forms.TypedChoiceField(
        choices=[(aro, f"Aro {aro}") for aro in (12, 16, 20, 24, 26, 27, 28, 29)],
        coerce=int,
        empty_value=None,
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_aro", "disabled": True}),
    )

    class Meta:
        model = Bicicleta
        fields = [
            "marca",
            "modelo_rel",
            "categoria_rel",
            "aro",
            "precio",
            "precio_oferta",
            "stock",
            "stock_minimo",
            "color",
            "descripcion",
            "especificaciones",
            "estado",
            "es_destacada",
            "es_oferta",
        ]
        widgets = {
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": MAX_PRECIO_CLP,
                    "maxlength": 8,
                    "inputmode": "numeric",
                    # Permite sólo números y limita visualmente a 8 caracteres (suficiente para 10 millones)
                    "oninput": "this.value = this.value.replace(/\\D/g, '').slice(0, 8)",
                }
            ),
            "precio_oferta": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": MAX_PRECIO_CLP,
                    "maxlength": 8,
                    "inputmode": "numeric",
                    "oninput": "this.value = this.value.replace(/\\D/g, '').slice(0, 8)",
                }
            ),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "especificaciones": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "es_destacada": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "es_oferta": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["modelo_rel"].label = "Modelo"
        self.fields["categoria_rel"].label = "Categoría"
        self.fields["aro"].label = "Aro"

        self.order_fields(
            [
                "marca",
                "modelo_rel",
                "categoria_rel",
                "aro",
                "precio",
                "precio_oferta",
                "stock",
                "stock_minimo",
                "color",
                "descripcion",
                "especificaciones",
                "estado",
                "es_destacada",
                "es_oferta",
            ]
        )

        # Textos de ayuda actualizados al nuevo tope de 10 millones
        self.fields["precio"].max_value = MAX_PRECIO_CLP
        self.fields["precio"].help_text = "Ingresa un valor entre $1 y $10.000.000 CLP."
        self.fields["precio_oferta"].max_value = MAX_PRECIO_CLP
        self.fields["precio_oferta"].help_text = "Máximo $10.000.000 CLP y menor que el precio normal."

        marca_id = None
        modelo_id = None

        if self.is_bound:
            marca_id = self.data.get("marca")
            modelo_id = self.data.get("modelo_rel")
        elif self.instance and self.instance.pk:
            if self.instance.modelo_rel_id:
                modelo_id = self.instance.modelo_rel_id
                marca_id = self.instance.modelo_rel.marca_id
            elif self.instance.modelo_rel:
                marca_id = self.instance.modelo_rel.marca_id

        if marca_id:
            self.fields["modelo_rel"].queryset = Modelo.objects.filter(
                marca_id=marca_id
            ).order_by("nombre")
            self.fields["modelo_rel"].empty_label = "Seleccione un modelo"
        else:
            self.fields["modelo_rel"].queryset = Modelo.objects.none()

        if modelo_id:
            try:
                modelo_inst = Modelo.objects.get(pk=modelo_id)
                if modelo_inst.categoria_id:
                    self.fields["categoria_rel"].queryset = Categoria.objects.filter(
                        pk=modelo_inst.categoria_id
                    )
                    self.fields["categoria_rel"].initial = modelo_inst.categoria_id
                else:
                    self.fields["categoria_rel"].queryset = Categoria.objects.filter(activa=True)
            except Modelo.DoesNotExist:
                pass
        
        self.fields["categoria_rel"].help_text = "Se autoselecciona según el modelo, pero puedes verificarla."

    def clean(self):
        cleaned_data = super().clean()
        marca = cleaned_data.get("marca")
        modelo = cleaned_data.get("modelo_rel")
        categoria = cleaned_data.get("categoria_rel")
        aro = cleaned_data.get("aro")

        if marca and modelo:
            if modelo.marca_id != marca.id:
                self.add_error(
                    "modelo_rel", "El modelo seleccionado no pertenece a la marca indicada."
                )

        if modelo and categoria:
            if modelo.categoria_id and modelo.categoria_id != categoria.id:
                self.add_error(
                    "categoria_rel",
                    f"La categoría '{categoria}' no corresponde al modelo '{modelo}'. "
                    f"Debe ser '{modelo.categoria}'.",
                )

        if modelo and aro:
            aro_esperado = None
            if "(Aro" in modelo.nombre:
                try:
                    parte_aros = modelo.nombre.split("(Aro")[-1].split(")")[0].strip()
                    if parte_aros.isdigit():
                        aro_esperado = int(parte_aros)
                except:
                    pass
            
            if aro_esperado and aro != aro_esperado:
                self.add_error(
                    "aro", f"El modelo '{modelo}' requiere aro {aro_esperado}. Has seleccionado {aro}."
                )

        return cleaned_data

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is not None:
            if precio <= 0:
                raise forms.ValidationError("El precio debe ser mayor que cero.")
            if precio > MAX_PRECIO_CLP:
                raise forms.ValidationError(f"El precio no puede superar los ${MAX_PRECIO_CLP:,.0f} CLP.")
        return precio

    def clean_precio_oferta(self):
        precio_oferta = self.cleaned_data.get("precio_oferta")
        precio = self.cleaned_data.get("precio")

        if precio_oferta is not None:
            if precio_oferta <= 0:
                raise forms.ValidationError("El precio de oferta debe ser mayor que cero.")
            if precio_oferta > MAX_PRECIO_CLP:
                raise forms.ValidationError(f"El precio de oferta no puede superar los ${MAX_PRECIO_CLP:,.0f} CLP.")
            if precio and precio_oferta >= precio:
                raise forms.ValidationError("El precio de oferta debe ser menor al precio normal.")
        return precio_oferta

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock no puede ser un valor negativo.")
        return stock

    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data.get("stock_minimo")
        if stock_minimo is not None and stock_minimo < 0:
            raise forms.ValidationError("El stock mínimo no puede ser un valor negativo.")
        return stock_minimo


# --- FORMULARIO DE FILTRADO SEGURO PARA EL CATÁLOGO ---
RANGOS_PRECIO_CHOICES = [
    ('', 'Todos los precios'),
    ('0-200000', 'Hasta $200.000 (Económica)'),
    ('200000-600000', '$200.000 a $600.000 (Media)'),
    ('600000-1500000', '$600.000 a $1.500.000 (Avanzada)'),
    ('1500000-5000000', '$1.500.000 a $5.000.000 (Pro)'),
    ('5000000-10000000', '$5.000.000 a $10.000.000+ (Elite)'),
]

class FiltroBicicletaForm(forms.Form):
    """Formulario blindado para validar los rangos del slider en el servidor"""
    rango_precio = forms.ChoiceField(
        choices=RANGOS_PRECIO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'id_rango_precio'})
    )
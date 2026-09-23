from django import forms
from .models import Bicicleta
import json


# Función auxiliar para obtener categorías con keys simples
def get_categorias_choices():
    """Retorna lista de tuplas (key_simple, nombre_mostrar) para categorías"""
    return [
        ('alta_gama', 'Alta Gama e Internacionales'),
        ('masivas_chile', 'Masivas y Populares en Chile'),
        ('urbanas_electricas', 'Urbanas, Plegables y Eléctricas'),
        ('bmx_freestyle', 'BMX y Freestyle'),
        ('otras', 'Otras / Genéricas'),
    ]


# Mapeo de keys simples a nombres completos del modelo
CATEGORIA_MAP = {
    'alta_gama': 'Alta Gama e Internacionales',
    'masivas_chile': 'Masivas y Populares en Chile',
    'urbanas_electricas': 'Urbanas, Plegables y Eléctricas',
    'bmx_freestyle': 'BMX y Freestyle',
    'otras': 'Otras',
}


# Mapeo inverso para validación
NOMBRE_A_KEY = {v: k for k, v in CATEGORIA_MAP.items()}


def get_marcas_por_categoria():
    """Retorna diccionario con marcas agrupadas por categoría (key simple)"""
    marcas_por_cat = {}
    for nombre_cat, marcas in Bicicleta.MARCA_CHOICES:
        key_simple = NOMBRE_A_KEY.get(nombre_cat)
        if key_simple:
            marcas_por_cat[key_simple] = [(marca, nombre) for marca, nombre in marcas]
    return marcas_por_cat


MARCAS_POR_CATEGORIA = get_marcas_por_categoria()


class BicicletaForm(forms.ModelForm):
    # Campo virtual para categoría (grupo de marcas) - usa keys simples
    categoria = forms.ChoiceField(
        choices=[('', 'Seleccione una categoría')] + get_categorias_choices(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_categoria'})
    )
    
    # Sobrescribimos el campo marca para usar Select con atributo id
    # Inicialmente vacío, se llena dinámicamente según categoría
    marca = forms.ChoiceField(
        choices=[('', 'Seleccione primero una categoría')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_marca'})
    )

    class Meta:
        model = Bicicleta
        fields = [
            "categoria",
            "marca",
            "modelo",
            "tipo",
            "aro",
            "precio",
            "stock",
            "color",
            "descripcion",
        ]
        widgets = {
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "aro": forms.NumberInput(
                attrs={"class": "form-control", "min": 10, "max": 29}
            ),
            "precio": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        marca = cleaned_data.get('marca')
        
        # Validar que la marca pertenezca a la categoría seleccionada
        if categoria and marca:
            marcas_validas = MARCAS_POR_CATEGORIA.get(categoria, [])
            marcas_validas_keys = [m[0] for m in marcas_validas]
            
            if marca not in marcas_validas_keys:
                raise forms.ValidationError(
                    f"La marca '{marca}' no corresponde a la categoría '{categoria}'."
                )
        elif not categoria:
            raise forms.ValidationError("Debe seleccionar una categoría.")
        elif not marca:
            raise forms.ValidationError("Debe seleccionar una marca.")
        
        return cleaned_data

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que cero.")
        return precio
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preparar datos para JavaScript - serializables
        self.marcas_por_categoria_json = {}
        for cat_key, marcas in MARCAS_POR_CATEGORIA.items():
            self.marcas_por_categoria_json[cat_key] = [
                {'value': marca, 'label': nombre} for marca, nombre in marcas
            ]
        
        # Si hay una categoría seleccionada (POST o instancia existente),
        # cargar las marcas correspondientes en el campo
        categoria_inicial = None
        if self.data:
            categoria_inicial = self.data.get('categoria')
        elif self.instance and self.instance.pk:
            # Para edición, necesitamos encontrar la categoría de la marca existente
            marca_actual = self.instance.marca if self.instance.marca else None
            if marca_actual:
                for cat_key, marcas in MARCAS_POR_CATEGORIA.items():
                    if any(m[0] == marca_actual for m in marcas):
                        categoria_inicial = cat_key
                        break
        
        if categoria_inicial and categoria_inicial in MARCAS_POR_CATEGORIA:
            marcas_cat = MARCAS_POR_CATEGORIA[categoria_inicial]
            self.fields['marca'].choices = [('', 'Seleccione una marca')] + marcas_cat
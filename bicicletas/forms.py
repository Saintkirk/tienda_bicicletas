from django import forms
from .models import (
    MAX_PRECIO_CLP,
    Bicicleta,
    Categoria,
    Cliente,
    Marca,
    Modelo,
    Venta,
)
import json


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
            # Obtenemos la instancia real del modelo desde el queryset
            instancia = value.instance if hasattr(value, 'instance') else value
            
            # ID de categoría asociada al modelo
            if instancia.categoria_id:
                option["attrs"]["data-categoria"] = str(instancia.categoria_id)
            
            # Lista de aros válidos (extraídos del nombre o de un campo si existiera)
            # Asumimos que el nombre del modelo puede contener el aro o usamos una lógica por defecto
            # Si tu modelo tiene un campo específico 'aros_sugeridos', úsalo aquí.
            # Por ahora, extraemos del nombre si sigue el patrón "Nombre (Aro X)" o dejamos todos si no.
            aros_validos = []
            if "(Aro" in instancia.nombre:
                try:
                    aro_str = instancia.nombre.split("(Aro")[-1].split(")")[0].strip()
                    if aro_str.isdigit():
                        aros_validos = [int(aro_str)]
                except:
                    pass
            
            # Si no hay aro específico en el nombre, podrías definir una lista por defecto según categoría
            if not aros_validos and instancia.categoria_id:
                # Lógica opcional: definir aros por defecto por categoría si no están en el nombre
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
        queryset=Modelo.objects.none(),  # Se llena dinámicamente en __init__ o vía AJAX
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
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "especificaciones": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "es_destacada": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "es_oferta": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Etiquetas claras
        self.fields["modelo_rel"].label = "Modelo"
        self.fields["categoria_rel"].label = "Categoría"
        self.fields["aro"].label = "Aro"

        # Ordenamiento de campos
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

        # Configuración de precios
        self.fields["precio"].max_value = MAX_PRECIO_CLP
        self.fields["precio"].help_text = "Ingresa un valor entre $1 y $99.999.999 CLP."
        self.fields["precio_oferta"].max_value = MAX_PRECIO_CLP
        self.fields["precio_oferta"].help_text = "Máximo $99.999.999 CLP y menor que el precio normal."

        # Lógica para inicializar querysets según si es edición o creación
        marca_id = None
        modelo_id = None

        if self.is_bound:
            # Datos enviados por POST
            marca_id = self.data.get("marca")
            modelo_id = self.data.get("modelo_rel")
        elif self.instance and self.instance.pk:
            # Edición de instancia existente
            if self.instance.modelo_rel_id:
                modelo_id = self.instance.modelo_rel_id
                marca_id = self.instance.modelo_rel.marca_id
            elif self.instance.modelo_rel:
                marca_id = self.instance.modelo_rel.marca_id

        # 1. Filtrar Modelos si hay Marca seleccionada
        if marca_id:
            self.fields["modelo_rel"].queryset = Modelo.objects.filter(
                marca_id=marca_id
            ).order_by("nombre")
            self.fields["modelo_rel"].empty_label = "Seleccione un modelo"
        else:
            self.fields["modelo_rel"].queryset = Modelo.objects.none()

        # 2. Si hay Modelo seleccionado (edición o POST), bloquear Categoría y Aro correspondientes
        if modelo_id:
            try:
                modelo_inst = Modelo.objects.get(pk=modelo_id)
                
                # Configurar Categoría
                if modelo_inst.categoria_id:
                    self.fields["categoria_rel"].queryset = Categoria.objects.filter(
                        pk=modelo_inst.categoria_id
                    )
                    self.fields["categoria_rel"].initial = modelo_inst.categoria_id
                    # No deshabilitamos el select en el servidor para permitir override si es necesario,
                    # pero en el frontend lo haremos readonly visualmente si se desea.
                else:
                    self.fields["categoria_rel"].queryset = Categoria.objects.filter(activa=True)

                # Configurar Aros (Lógica de extracción del nombre o lista fija)
                # Aquí preparamos los datos para que el JS los lea si es necesario, 
                # pero el valor inicial ya está en self.initial si existe.
                
            except Modelo.DoesNotExist:
                pass
        
        # Ayudas de texto
        self.fields["categoria_rel"].help_text = "Se autoselecciona según el modelo, pero puedes verificarla."

    def clean(self):
        cleaned_data = super().clean()
        marca = cleaned_data.get("marca")
        modelo = cleaned_data.get("modelo_rel")
        categoria = cleaned_data.get("categoria_rel")
        aro = cleaned_data.get("aro")

        # Validación Marca-Modelo
        if marca and modelo:
            if modelo.marca_id != marca.id:
                self.add_error(
                    "modelo_rel", "El modelo seleccionado no pertenece a la marca indicada."
                )

        # Validación Modelo-Categoría
        if modelo and categoria:
            if modelo.categoria_id and modelo.categoria_id != categoria.id:
                self.add_error(
                    "categoria_rel",
                    f"La categoría '{categoria}' no corresponde al modelo '{modelo}'. "
                    f"Debe ser '{modelo.categoria}'.",
                )

        # Validación Modelo-Aro
        if modelo and aro:
            # Intentar extraer aro esperado del nombre del modelo
            aro_esperado = None
            if "(Aro" in modelo.nombre:
                try:
                    parte_aros = modelo.nombre.split("(Aro")[-1].split(")")[0].strip()
                    if parte_aros.isdigit():
                        aro_esperado = int(parte_aros)
                except:
                    pass
            
            # Si el modelo define un aro específico, validar
            if aro_esperado and aro != aro_esperado:
                self.add_error(
                    "aro", f"El modelo '{modelo}' requiere aro {aro_esperado}. Has seleccionado {aro}."
                )

        return cleaned_data

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que cero.")
        return precio

    def clean_precio_oferta(self):
        precio_oferta = self.cleaned_data.get("precio_oferta")
        precio = self.cleaned_data.get("precio")

        if precio_oferta and precio:
            if precio_oferta >= precio:
                raise forms.ValidationError("El precio de oferta debe ser menor al precio normal.")
        return precio_oferta


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "apellido", "email", "telefono", "direccion", "ciudad"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "ciudad": forms.TextInput(attrs={"class": "form-control"}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente", "metodo_pago", "descuento", "impuesto", "notas"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "metodo_pago": forms.Select(attrs={"class": "form-select"}),
            "descuento": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "impuesto": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class CarritoForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )
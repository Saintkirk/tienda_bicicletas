from django import forms
from .models import Bicicleta, Cliente, Venta


class BicicletaForm(forms.ModelForm):
    """Formulario para gestión de bicicletas"""

    class Meta:
        model = Bicicleta
        fields = [
            "modelo_rel", 
            "tipo", 
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
            "modelo_rel": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "categoria_rel": forms.Select(attrs={"class": "form-select"}),
            "aro": forms.NumberInput(attrs={"class": "form-control", "min": 10, "max": 29}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "precio_oferta": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "especificaciones": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "es_destacada": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "es_oferta": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

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
    """Formulario para clientes"""

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
    """Formulario para registrar ventas"""

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
    """Formulario para actualizar carrito"""

    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )
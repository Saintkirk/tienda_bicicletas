from django import forms
from .models import Bicicleta


class BicicletaForm(forms.ModelForm):
    class Meta:
        model = Bicicleta
        fields = [
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
            "marca": forms.TextInput(attrs={"class": "form-control"}),
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "aro": forms.NumberInput(attrs={"class": "form-control", "min": 12, "max": 80}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_marca(self):
        marca = self.cleaned_data["marca"].strip()
        if len(marca) < 2:
            raise forms.ValidationError("La marca debe tener al menos 2 caracteres.")
        return marca

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que cero.")
        return precio
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
        # Cambiamos TextInput por Select para que despliegue las opciones agrupadas
        "marca": forms.Select(attrs={"class": "form-select"}),
        "modelo": forms.TextInput(attrs={"class": "form-control"}),
        "tipo": forms.Select(attrs={"class": "form-select"}),
        # Ajustamos el aro según la validación del modelo (10 a 29)
        "aro": forms.NumberInput(
            attrs={"class": "form-control", "min": 10, "max": 29}
        ),
        "precio": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        "color": forms.TextInput(attrs={"class": "form-control"}),
        "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    }

  # Como 'marca' ahora es un selector de opciones fijas,
  # ya no necesitamos la validación de texto libre (clean_marca).

  def clean_precio(self):
    precio = self.cleaned_data["precio"]
    if precio <= 0:
      raise forms.ValidationError("El precio debe ser mayor que cero.")
    return precio
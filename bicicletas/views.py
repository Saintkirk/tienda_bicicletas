from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.http import JsonResponse
import json

from .forms import BicicletaForm, FiltroBicicletaForm
from .models import Bicicleta, Categoria, Marca, Modelo


class InicioView(TemplateView):
    """Página de inicio con estadísticas y productos destacados"""
    template_name = "bicicletas/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_bicicletas"] = Bicicleta.objects.count()
        context["bicicletas_destacadas"] = Bicicleta.objects.filter(
            es_destacada=True, stock__gt=0
        )[:6]
        context["bicicletas_oferta"] = Bicicleta.objects.filter(
            es_oferta=True, stock__gt=0
        )[:4]
        context["categorias"] = Categoria.objects.filter(activa=True)
        context["bajo_stock"] = Bicicleta.objects.filter(
            estado="BAJO_STOCK"
        ).count()
        context["agotados"] = Bicicleta.objects.filter(estado="AGOTADO").count()
    
        return context


class ListaBicicletasView(ListView):
    """Lista todas las bicicletas con filtros y búsqueda"""
    model = Bicicleta
    template_name = "bicicletas/lista.html"
    context_object_name = "bicicletas"
    paginate_by = 12

    def get_queryset(self):
        # Optimización: select_related para evitar consultas N+1
        queryset = Bicicleta.objects.select_related(
            "categoria_rel", "modelo_rel__marca"
        ).all()

        # Filtro por búsqueda general (q)
        busqueda = self.request.GET.get("q")
        if busqueda:
            queryset = queryset.filter(
                Q(modelo_rel__nombre__icontains=busqueda)
                | Q(modelo_rel__marca__nombre__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
                | Q(color__icontains=busqueda)
            )

        # Filtro por Categoría (ID)
        categoria_id = self.request.GET.get("categoria")
        if categoria_id:
            queryset = queryset.filter(categoria_rel_id=categoria_id)

        # Filtro por Marca (ID)
        marca_id = self.request.GET.get("marca")
        if marca_id:
            queryset = queryset.filter(modelo_rel__marca_id=marca_id)

        # Filtro por Modelo (ID)
        modelo_id = self.request.GET.get("modelo")
        if modelo_id:
            queryset = queryset.filter(modelo_rel_id=modelo_id)

        # Filtro por Aro (Valor entero)
        aro = self.request.GET.get("aro")
        if aro:
            queryset = queryset.filter(aro=aro)

        # Filtro por Estado
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtro por Tipo (si existe en tu modelo)
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # --- FILTRO DE PRECIOS BLINDADO CON FORMULARIO DE DJANGO ---
        form_filtro = FiltroBicicletaForm(self.request.GET)
        if form_filtro.is_valid():
            rango = form_filtro.cleaned_data.get("rango_precio")
            if rango:
                try:
                    min_val, max_val = rango.split("-")
                    queryset = queryset.filter(precio__gte=int(min_val), precio__lte=int(max_val))
                except (ValueError, TypeError):
                    pass

        # Solo disponibles (Stock > 0)
        solo_disponibles = self.request.GET.get("disponibles")
        if solo_disponibles and solo_disponibles.lower() in ['true', '1', 'on']:
            queryset = queryset.filter(stock__gt=0)

        # Ordenamiento
        orden = self.request.GET.get("orden", "-fecha_ingreso")
        campos_validos = ['precio', '-precio', 'modelo_rel__nombre', '-modelo_rel__nombre', 'fecha_ingreso', '-fecha_ingreso']
        if orden in campos_validos:
            queryset = queryset.order_by(orden)
        else:
            queryset = queryset.order_by("-fecha_ingreso")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos el formulario blindado para renderizar el select en el HTML de forma segura
        context["form_filtro"] = FiltroBicicletaForm(self.request.GET)
        context["categorias"] = Categoria.objects.filter(activa=True).order_by("nombre")
        context["marcas"] = Marca.objects.order_by("nombre")
        context["modelos"] = Modelo.objects.select_related("marca").order_by(
            "marca__nombre", "nombre"
        )
        context["aros"] = [12, 16, 20, 24, 26, 27, 28, 29]
        context["tipos"] = getattr(Bicicleta, 'TIPO_CHOICES', [])
        context["estados"] = getattr(Bicicleta, 'ESTADO_CHOICES', [])
        
        context["request_get"] = self.request.GET
        
        return context


class DetalleBicicletaView(DetailView):
    """Detalle de una bicicleta específica"""
    model = Bicicleta
    template_name = "bicicletas/detalle.html"
    context_object_name = "bicicleta"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bicicleta = self.object
        filtros = Q(categoria_rel=bicicleta.categoria_rel)
        if bicicleta.modelo_rel_id:
            filtros |= Q(modelo_rel__marca_id=bicicleta.modelo_rel.marca_id)
        
        context["relacionados"] = Bicicleta.objects.filter(
            filtros, stock__gt=0
        ).exclude(pk=bicicleta.pk)[:4]
        return context


class CrearBicicletaView(CreateView):
    """Crear nueva bicicleta"""
    model = Bicicleta
    form_class = BicicletaForm
    template_name = "bicicletas/crear.html"
    success_url = reverse_lazy("lista_bicicletas")

    def form_valid(self, form):
        messages.success(self.request, "La bicicleta fue creada correctamente.")
        return super().form_valid(form)


class EditarBicicletaView(UpdateView):
    """Editar bicicleta existente"""
    model = Bicicleta
    form_class = BicicletaForm
    template_name = "bicicletas/editar.html"
    success_url = reverse_lazy("lista_bicicletas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bicicleta = self.object
        
        if bicicleta.modelo_rel:
            context['initial_modelo_id'] = bicicleta.modelo_rel.id
            context['initial_marca_id'] = bicicleta.modelo_rel.marca_id
        
        if bicicleta.categoria_rel:
            context['initial_categoria_id'] = bicicleta.categoria_rel.id
            context['initial_categoria_nombre'] = bicicleta.categoria_rel.nombre
            
        context['initial_aro'] = bicicleta.aro
        
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "La bicicleta fue modificada correctamente."
        )
        return super().form_valid(form)


class EliminarBicicletaView(DeleteView):
    """Eliminar bicicleta individual"""
    model = Bicicleta
    template_name = "bicicletas/eliminar.html"
    success_url = reverse_lazy("lista_bicicletas")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nombre_obj = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"La bicicleta '{nombre_obj}' ha sido eliminada correctamente.")
        return response


def eliminar_multiple_bicicletas(request):
    """Elimina múltiples bicicletas seleccionadas desde el listado con transacción atómica."""
    if request.method == "POST":
        # CORREGIDO: Cambiado de 'bicicleta_ids' a 'selected_items' para calzar con el HTML
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            messages.warning(request, "No se seleccionaron bicicletas para eliminar.")
            return redirect("lista_bicicletas")
        
        try:
            with transaction.atomic():
                queryset = Bicicleta.objects.filter(pk__in=selected_ids)
                count = queryset.count()
                
                if count == 0:
                    messages.warning(request, "Las bicicletas seleccionadas no existen o ya fueron eliminadas.")
                    return redirect("lista_bicicletas")
                
                queryset.delete()
                messages.success(request, f"Se eliminaron {count} bicicleta(s) correctamente.")
                
        except Exception as e:
            messages.error(request, "Ocurrió un error al intentar eliminar las bicicletas. No se realizaron cambios.")
            
    return redirect("lista_bicicletas")


def obtener_modelos_por_marca(request):
    """Devuelve modelos, categorías y aros sugeridos según la marca seleccionada."""
    marca_id = request.GET.get('marca_id')
    
    if not marca_id:
        return JsonResponse({'error': 'Falta ID de marca'}, status=400)

    try:
        modelos = Modelo.objects.filter(marca_id=marca_id).select_related('categoria')
        datos_modelos = []
        
        for m in modelos:
            aros_sugeridos = []
            if "(Aro" in m.nombre:
                try:
                    parte_aros = m.nombre.split("(Aro")[-1].split(")")[0].strip()
                    if parte_aros.isdigit():
                        aros_sugeridos = [int(parte_aros)]
                except (IndexError, ValueError):
                    pass
            
            datos_modelos.append({
                'id': m.id,
                'nombre': m.nombre,
                'categoria_id': m.categoria_id,
                'categoria_nombre': m.categoria.nombre if m.categoria else '',
                'aros_sugeridos': aros_sugeridos
            })
            
        return JsonResponse({'modelos': datos_modelos})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
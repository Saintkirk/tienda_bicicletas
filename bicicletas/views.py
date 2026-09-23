from django.contrib import messages
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

from .forms import BicicletaForm, CarritoForm, VentaForm
from .models import Bicicleta, CarritoItem, Categoria, ItemVenta, Marca, Modelo, Venta


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

        # Estadísticas de ventas
        ventas_mes = Venta.objects.filter(fecha_venta__month__gte=1).count()
        context["ventas_totales"] = ventas_mes

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

        # Rango de Precios
        precio_min = self.request.GET.get("precio_min")
        precio_max = self.request.GET.get("precio_max")
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)

        # Solo disponibles (Stock > 0)
        solo_disponibles = self.request.GET.get("disponibles")
        if solo_disponibles and solo_disponibles.lower() in ['true', '1', 'on']:
            queryset = queryset.filter(stock__gt=0)

        # Ordenamiento
        orden = self.request.GET.get("orden", "-fecha_ingreso")
        # Validar que el orden sea seguro para evitar inyección SQL simple
        campos_validos = ['precio', '-precio', 'modelo_rel__nombre', '-modelo_rel__nombre', 'fecha_ingreso', '-fecha_ingreso']
        if orden in campos_validos:
            queryset = queryset.order_by(orden)
        else:
            queryset = queryset.order_by("-fecha_ingreso")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos las listas para los filtros del sidebar/header
        context["categorias"] = Categoria.objects.filter(activa=True).order_by("nombre")
        context["marcas"] = Marca.objects.order_by("nombre")
        context["modelos"] = Modelo.objects.select_related("marca").order_by(
            "marca__nombre", "nombre"
        )
        context["aros"] = [12, 16, 20, 24, 26, 27, 28, 29]
        context["tipos"] = getattr(Bicicleta, 'TIPO_CHOICES', [])
        context["estados"] = getattr(Bicicleta, 'ESTADO_CHOICES', [])
        
        # Mantener los valores actuales en el contexto para que el formulario los recuerde
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
        """
        Inyectamos datos adicionales para que el JavaScript pueda 
        restaurar la categoría y el aro al cargar la página de edición.
        """
        context = super().get_context_data(**kwargs)
        bicicleta = self.object
        
        # Pasamos los IDs actuales para que JS los use al cargar
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


# --- FUNCIÓN: ELIMINACIÓN MÚLTIPLE ---
def eliminar_multiple_bicicletas(request):
    """
    Elimina múltiples bicicletas seleccionadas desde el listado.
    IMPORTANTE: Debe coincidir con el name='bicicleta_ids' del HTML/JS.
    """
    if request.method == "POST":
        selected_ids = request.POST.getlist('bicicleta_ids')
        
        if not selected_ids:
            messages.warning(request, "No se seleccionaron bicicletas para eliminar.")
            return redirect("lista_bicicletas")
        
        queryset = Bicicleta.objects.filter(pk__in=selected_ids)
        count = queryset.count()
        
        if count == 0:
            messages.warning(request, "Las bicicletas seleccionadas no existen o ya fueron eliminadas.")
            return redirect("lista_bicicletas")
        
        queryset.delete()
        messages.success(request, f"Se eliminaron {count} bicicleta(s) correctamente.")
        
    return redirect("lista_bicicletas")


# --- VISTA AJAX PARA FILTRADO DINÁMICO ---
def obtener_modelos_por_marca(request):
    """
    Devuelve modelos, categorías y aros sugeridos según la marca seleccionada.
    Uso: GET /bicicletas/api/modelos-por-marca/?marca_id=X
    """
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
                except:
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


class CarritoView(TemplateView):
    """Vista del carrito de compras"""
    template_name = "bicicletas/carrito.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        items = CarritoItem.objects.filter(session_key=session_key).select_related(
            "bicicleta"
        )
        context["items"] = items
        context["total"] = sum(item.subtotal for item in items)
        context["total_items"] = sum(item.cantidad for item in items)
        return context


def agregar_al_carrito(request, pk):
    """Agregar bicicleta al carrito"""
    bicicleta = get_object_or_404(Bicicleta, pk=pk)

    if bicicleta.stock == 0:
        messages.error(request, "Producto agotado")
        return redirect("lista_bicicletas")

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    carrito_item, creado = CarritoItem.objects.get_or_create(
        session_key=session_key, bicicleta=bicicleta, defaults={"cantidad": 1}
    )

    if not creado:
        if carrito_item.cantidad < bicicleta.stock:
            carrito_item.cantidad += 1
            carrito_item.save()
            messages.success(
                request,
                f"Cantidad aumentada. Ahora tienes {carrito_item.cantidad} en el carrito.",
            )
        else:
            messages.warning(request, "No hay más stock disponible")
    else:
        messages.success(request, "Producto agregado al carrito")

    return redirect("carrito")


def eliminar_del_carrito(request, pk):
    """Eliminar item del carrito"""
    session_key = request.session.session_key
    if session_key:
        count, _ = CarritoItem.objects.filter(
            session_key=session_key, bicicleta_id=pk
        ).delete()
        if count > 0:
            messages.success(request, "Producto eliminado del carrito")
        else:
            messages.warning(request, "El producto no estaba en el carrito")
    return redirect("carrito")


def actualizar_carrito(request, pk):
    """Actualizar cantidad en el carrito"""
    if request.method == "POST":
        cantidad = int(request.POST.get("cantidad", 1))
        session_key = request.session.session_key

        if session_key and cantidad > 0:
            item = get_object_or_404(
                CarritoItem, session_key=session_key, bicicleta_id=pk
            )

            if cantidad <= item.bicicleta.stock:
                item.cantidad = cantidad
                item.save()
                messages.success(request, "Carrito actualizado")
            else:
                messages.error(
                    request,
                    f"Stock máximo disponible: {item.bicicleta.stock}",
                )

    return redirect("carrito")


class CrearVentaView(CreateView):
    """Procesar venta desde el carrito"""
    model = Venta
    form_class = VentaForm
    template_name = "bicicletas/crear_venta.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.session_key
        if session_key:
            context["items"] = CarritoItem.objects.filter(
                session_key=session_key
            ).select_related("bicicleta")
            context["total"] = sum(item.subtotal for item in context["items"])
        return context

    def form_valid(self, form):
        session_key = self.request.session.session_key
        if not session_key:
            messages.error(self.request, "Error de sesión")
            return redirect("lista_bicicletas")

        items = CarritoItem.objects.filter(session_key=session_key).select_related(
            "bicicleta"
        )
        if not items.exists():
            messages.error(self.request, "El carrito está vacío")
            return redirect("carrito")

        # Crear venta
        venta = form.save(commit=False)
        venta.numero_venta = f"VEN-{Venta.objects.count() + 1:06d}"
        venta.subtotal = sum(item.subtotal for item in items)
        venta.total = venta.subtotal - venta.descuento + venta.impuesto
        venta.save()

        # Crear items de venta y reducir stock
        for item in items:
            ItemVenta.objects.create(
                venta=venta,
                bicicleta=item.bicicleta,
                cantidad=item.cantidad,
                precio_unitario=item.bicicleta.precio_final,
                subtotal=item.subtotal,
            )
            item.bicicleta.reducir_stock(item.cantidad)

        # Limpiar carrito
        items.delete()

        messages.success(
            self.request,
            f"Venta #{venta.numero_venta} creada exitosamente. Total: ${venta.total}",
        )
        return redirect("detalle_venta", pk=venta.pk)


class DetalleVentaView(DetailView):
    """Detalle de una venta"""
    model = Venta
    template_name = "bicicletas/detalle_venta.html"
    context_object_name = "venta"


class ListaVentasView(ListView):
    """Lista todas las ventas"""
    model = Venta
    template_name = "bicicletas/lista_ventas.html"
    context_object_name = "ventas"
    paginate_by = 20
    ordering = ["-fecha_venta"]
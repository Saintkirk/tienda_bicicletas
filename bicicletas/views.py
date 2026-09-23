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
        queryset = Bicicleta.objects.select_related(
            "categoria_rel", "modelo_rel__marca"
        ).all()

        # Filtro por búsqueda
        busqueda = self.request.GET.get("q")
        if busqueda:
            queryset = queryset.filter(
                Q(modelo_rel__nombre__icontains=busqueda)
                | Q(modelo_rel__marca__nombre__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
            )

        # Filtro por tipo
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # Filtro por categoría
        categoria = self.request.GET.get("categoria")
        if categoria:
            queryset = queryset.filter(categoria_rel_id=categoria)

        marca = self.request.GET.get("marca")
        if marca:
            queryset = queryset.filter(modelo_rel__marca_id=marca)

        modelo = self.request.GET.get("modelo")
        if modelo:
            queryset = queryset.filter(modelo_rel_id=modelo)

        aro = self.request.GET.get("aro")
        if aro:
            queryset = queryset.filter(aro=aro)

        # Filtro por estado
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtro por rango de precio
        precio_min = self.request.GET.get("precio_min")
        precio_max = self.request.GET.get("precio_max")
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)

        # Filtro solo disponibles
        solo_disponibles = self.request.GET.get("disponibles")
        if solo_disponibles:
            queryset = queryset.filter(stock__gt=0)

        # Ordenamiento
        orden = self.request.GET.get("orden", "-fecha_ingreso")
        queryset = queryset.order_by(orden)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.filter(activa=True)
        context["marcas"] = Marca.objects.order_by("nombre")
        context["modelos"] = Modelo.objects.select_related("marca").order_by(
            "marca__nombre", "nombre"
        )
        context["aros"] = [20, 24, 26, 27, 28, 29]
        context["tipos"] = Bicicleta.TIPO_CHOICES
        context["estados"] = Bicicleta.ESTADO_CHOICES
        return context


class DetalleBicicletaView(DetailView):
    """Detalle de una bicicleta específica"""

    model = Bicicleta
    template_name = "bicicletas/detalle.html"
    context_object_name = "bicicleta"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bicicleta = self.object
        filtros = Q(tipo=bicicleta.tipo)
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

    def form_valid(self, form):
        messages.success(
            self.request, "La bicicleta fue modificada correctamente."
        )
        return super().form_valid(form)


class EliminarBicicletaView(DeleteView):
    """Eliminar bicicleta"""

    model = Bicicleta
    template_name = "bicicletas/eliminar.html"
    success_url = reverse_lazy("lista_bicicletas")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La bicicleta fue eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


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
        CarritoItem.objects.filter(
            session_key=session_key, bicicleta_id=pk
        ).delete()
        messages.success(request, "Producto eliminado del carrito")
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
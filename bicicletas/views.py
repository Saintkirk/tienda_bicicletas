from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BicicletaForm
from .models import Bicicleta


def inicio(request):
    total_bicicletas = Bicicleta.objects.count()
    return render(
        request,
        "bicicletas/inicio.html",
        {"total_bicicletas": total_bicicletas},
    )


def lista_bicicletas(request):
    bicicletas = Bicicleta.objects.all()
    return render(
        request,
        "bicicletas/lista.html",
        {"bicicletas": bicicletas},
    )


def crear_bicicleta(request):
    if request.method == "POST":
        form = BicicletaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La bicicleta fue creada correctamente.")
            return redirect("lista_bicicletas")
    else:
        form = BicicletaForm()

    return render(
        request,
        "bicicletas/crear.html",
        {"form": form},
    )


def editar_bicicleta(request, pk):
    bicicleta = get_object_or_404(Bicicleta, pk=pk)

    if request.method == "POST":
        form = BicicletaForm(request.POST, instance=bicicleta)
        if form.is_valid():
            form.save()
            messages.success(request, "La bicicleta fue modificada correctamente.")
            return redirect("lista_bicicletas")
    else:
        form = BicicletaForm(instance=bicicleta)

    return render(
        request,
        "bicicletas/editar.html",
        {"form": form, "bicicleta": bicicleta},
    )


def eliminar_bicicleta(request, pk):
    bicicleta = get_object_or_404(Bicicleta, pk=pk)

    if request.method == "POST":
        bicicleta.delete()
        messages.success(request, "La bicicleta fue eliminada correctamente.")
        return redirect("lista_bicicletas")

    return render(
        request,
        "bicicletas/eliminar.html",
        {"bicicleta": bicicleta},
    )
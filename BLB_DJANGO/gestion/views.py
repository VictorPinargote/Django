from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Libro, Autor, Prestamo, multa
from django.conf import settings

# Create your views here.
def index(request):
    title = settings.TITLE
    
    return render(request, 'gestion/templates/index.html', {'titulo': title})

def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'gestion/templates/libros.html', {'libros': libros})

def crear_libro(request):
    autores = Autor.objects.all()
    
    if request.method == 'POST': #si ya envia datos y captura en variabes para poder crear el libro
        titulo = request.POST.get('titulo')
        autor_id = request.POST.get('autor')
        if titulo and autor_id:
            autor = get_object_or_404(Autor, id=autor_id)
            Libro.objects.create(titulo=titulo, autor=autor)
            return redirect('lista_libros')
    return render(request, 'gestion/templates/crear_libros.html', {'autores': autores})

def lista_prestamo(request):
    prestamos = multa.objects.all()
    return render(request, 'gestion/templates/prestamos.html', {'prestamos': prestamos})

def lista_crear_prestamo(request):
    prestamos = Prestamo.objects.all()
    
    if request.mesthod == 'POST':
        Libro == request.POST.get('libro')
        

def lista_autores(request):
    autores = Autor.objects.all()
    return render(request, 'gestion/templates/autores.html', {'autores': autores})

def crear_autor(request):
    if request.method == 'POST': #si ya envia datos y captura en variabes para poder crear el autor
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        return redirect('lista_autores')
        
    return render(request, 'gestion/templates/crear_autores.html')

def lista_multas(request):
    multas = multa.objects.all()
    return render(request, 'gestion/templates/multas.html', {'multas': multas})

def crear_multa(request, prestamo_id):
    pass

def detalle_prestamo(request, id):
    pass


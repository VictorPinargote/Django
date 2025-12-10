from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone  
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Autor, Libro, Prestamo, Multa


def index(request):
    titulo2 = "hola mundillo"
    title = settings.TITLE
    return render(request, 'gestion/templates/home.html', {'titulo': title, 't': titulo2})

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
    prestamos = Prestamo.objects.all()
    return render(request, 'gestion/templates/prestamos.html', {'prestamos': prestamos})

def lista_crear_prestamo(request):
    prestamos = Prestamo.objects.all()
    
    if request.mesthod == 'POST':
        Libro == request.POST.get('libro')
        

def lista_autores(request):
    autores = Autor.objects.all()
    return render(request, 'gestion/templates/autores.html', {'autores': autores})


def crear_autor(request, id=None):
    if id == None:  # Crear nuevo autor
        autor = None
        modo = 'crear'
    else:  # Editar autor existente
        autor = get_object_or_404(Autor, id=id)
        modo = 'editar'
        
    if request.method == 'POST': #si ya envia datos y captura en variabes para poder crear el autor
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        if autor == None:
            Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        else:
            autor.nombre = nombre
            autor.apellido = apellido
            autor.bibliografia = bibliografia
            autor.save()
        return redirect('lista_autores')
    context = {'autor': autor,
               'titulo': 'editar autor' if modo == 'editar' else 'Crear autor',
               'texto_boton': 'Guardar cambios' if modo == 'editar' else 'Crear'}
    return render(request, 'gestion/templates/crear_autor.html', context)

def lista_multas(request):
    multas = Multa.objects.all()
    return render(request, 'gestion/templates/multas.html', {'multas': multas})

def crear_multa(request, prestamo_id):
    pass

def detalle_prestamo(request, id):
    pass

@login_required #asegura que el usuario este logueado
def crear_prestamo(request):
    if not request.user.has_perm('gestion.gestionar_prestamos'):
        return HttpResponseForbidden("No tienes permiso para crear préstamos.")
    libro = Libro.objects.filter(disponible=True)
    usuarios = User.objects.all()
    if request.method == 'POST':
        libro_id = request.POST.get('libro')
        usuario_id = request.POST.get('usuario')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        if libro_id and usuario_id and fecha_prestamo:
            libro = get_object_or_404(Libro, id=libro_id)
            usuario = get_object_or_404(User, id=usuario_id)
            prestamo = Prestamo.objects.create(libro=libro, 
                                               usuario=usuario, 
                                               fecha_prestamo=fecha_prestamo)
            libro.disponible = False
            libro.save()
            return redirect('detalle_prestamo', id=prestamo.id)
    fecha = (timezone.now()).date().isoformat() # YYYY-MM-DD este se captura l aparte de al fehc actual
    return render(request, 'gestion/templates/crear_prestamo.html', {'libros': libro, 
                                                                     'usuarios': usuarios,
                                                                     'fecha': fecha})

def editar_autor(request, id):
    autor = get_object_or_404(Autor, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        
        if nombre and apellido:
            autor.apellido = apellido
            autor.nombre = nombre
            autor.bibliografia = bibliografia
            autor.save()
            return redirect('lista_autores')
    
    return render(request, 'gestion/templates/editar_autor.html', {'autor': autor})

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'gestion/templates/registro.html', {form: form})

# Create your views here.





#
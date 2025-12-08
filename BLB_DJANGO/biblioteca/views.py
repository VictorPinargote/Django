from django.shortcuts import render
from .models import Libro, Autor
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
def crear_libro(request):
    autores = Autor.objects.all()
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        isbn = request.POST.get('isbn')
        autor_id = request.POST.get('autor')
        autor = get_object_or_404(Autor, id=autor_id)
        if titulo and isbn and autor:
            Libro.objects.create(titulo=titulo, isbn=isbn, autor=autor)
            return redirect('lista_libros')
    
    return render(request, 'gestion/templates/crear_libro.html', {'autores': autores})
    
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
        
            
            
def listar_libros(request):
    libros = Libro.objects.all()
    return render(request, 'gestion/templates/libros.html', {'libros': libros})

def crear_autor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        return redirect('lista_autores')
    
    return render(request, 'gestion/templates/crear_autor.html')
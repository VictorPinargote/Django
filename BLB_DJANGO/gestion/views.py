from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import login
from functools import wraps
from .openlibrary import buscar_libros, buscar_autores

from .models import Autor, Libro, Prestamo, Multa, Perfil
from .forms import RegistroUsuarioForm

# ============================================
# SISTEMA DE PERMISOS POR ROLES
# ============================================
# Roles: usuario, bodeguero, bibliotecario, admin, superusuario
# - usuario: Ver todo, pagar SUS multas, solicitar préstamos
# - bodeguero: Crear/editar libros y autores  
# - bibliotecario: Gestionar préstamos
# - admin: Ver reportes, gestionar multas
# - superusuario: Acceso total

def obtener_rol(user):
    """Obtiene el rol del usuario, retorna 'usuario' si no tiene perfil"""
    if not user.is_authenticated:
        return None
    try:
        return user.perfil.rol
    except:
        return 'usuario'

def tiene_permiso(user, roles_permitidos):
    """Verifica si el usuario tiene alguno de los roles permitidos"""
    rol = obtener_rol(user)
    if rol is None:
        return False
    if rol == 'superusuario':  # Superusuario tiene acceso total
        return True
    return rol in roles_permitidos

def requiere_rol(*roles_permitidos):
    """Decorador para proteger vistas por rol"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not tiene_permiso(request.user, roles_permitidos):
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def index(request):
    titulo2 = "Hola Mundillo y sapos"
    title = settings.TITLE
    return render(request, 'gestion/templates/home.html', {'titulo': title, 't': titulo2})

def lista_libros(request):
    libros = Libro.objects.all()
    return render(request, 'gestion/templates/libros.html', {'libros': libros})

@requiere_rol('bodeguero', 'admin')
def crear_libro(request):
    autores = Autor.objects.all()
    if request.method == "POST": #si ya envia datos y captura en variabes para poder crear el libro
        titulo =  request.POST.get('titulo')
        autor_id =  request.POST.get('autor')
        
        if titulo and autor_id:
            autor = get_object_or_404(Autor, id=autor_id)
            Libro.objects.create(titulo=titulo, autor=autor)
            return redirect('lista_libros')
    return render(request, 'gestion/templates/crear_libros.html', {'autores': autores})

def lista_prestamos(request):
    prestamos = Prestamo.objects.all()
    return render(request, 'gestion/templates/prestamos.html', {'prestamos': prestamos})

def lista_autores(request):
    autores = Autor.objects.all()
    return render(request, 'gestion/templates/autores.html', {'autores': autores})
        
@requiere_rol('bodeguero', 'admin')
def crear_autor(request, id=None):
    if id == None:
        autor = None
        modo = 'crear'
    else:
        autor = get_object_or_404(Autor, id=id)
        modo = 'editar'
        
    if request.method == 'POST': #si ya envia datos y captura en variabes para poder crear el autor
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        bibliografia = request.POST.get('bibliografia')
        if autor == None:
            Autor.objects.create(nombre=nombre, apellido=apellido, bibliografia=bibliografia)
        else:
            autor.apellido = apellido
            autor.nombre = nombre
            autor.bibliografia = bibliografia
            autor.save()
        return redirect('lista_autores')
    context = {'autor': autor,
               'titulo': 'Editar Autor' if modo == 'editar' else 'Crear Autor',
               'texto_boton': 'Guardar cambios' if modo == 'editar' else 'Crear'}
    return render(request, 'gestion/templates/crear_autores.html', context)

def lista_multas(request):
    multas = Multa.objects.all()
    return render(request, 'gestion/templates/multas.html', {'multas': multas})

@requiere_rol('bibliotecario', 'admin')
def crear_prestamo(request):
    libro = Libro.objects.filter(disponible=True)
    usuario = User.objects.all()
    if request.method == 'POST':
        libro_id = request.POST.get('libro')
        usuario_id = request.POST.get('usuario')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        fecha_max = request.POST.get('fecha_max')
        if libro_id and usuario_id and fecha_prestamo and fecha_max:
            libro = get_object_or_404(Libro, id=libro_id)
            usuario = get_object_or_404(User, id=usuario_id)
            prestamo = Prestamo.objects.create(libro = libro,
                                               usuario=usuario,
                                               fecha_prestamos=fecha_prestamo,
                                               fecha_max=fecha_max)
            libro.disponible = False
            libro.save()
            return redirect('detalle_prestamo', id=prestamo.id)
    fecha = (timezone.now().date()).isoformat() # YYYY-MM-DD este se captura l aparte de al fehc actual
    return render(request, 'gestion/templates/crear_prestamo.html', {'libros': libro,
                                                                     'usuarios': usuario,
                                                                     'fecha': fecha})

@requiere_rol('bodeguero', 'admin')
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

# Códigos de verificación para roles especiales
CODIGOS_ROL = {
    'usuario': None,  # No requiere código
    'bodeguero': 'bodega123',
    'bibliotecario': 'biblio123',
    'admin': 'admin123',
    'superusuario': 'super123',
}

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            rol_seleccionado = form.cleaned_data.get('rol')
            codigo_ingresado = form.cleaned_data.get('codigo_rol')
            codigo_requerido = CODIGOS_ROL.get(rol_seleccionado)
            
            # Validar código si el rol lo requiere
            if codigo_requerido is not None and codigo_ingresado != codigo_requerido:
                form.add_error('codigo_rol', f'Código incorrecto para el rol {rol_seleccionado}')
                return render(request, 'gestion/templates/registration/registro.html', {'form': form})
            
            usuario = form.save()  # guarda el usuario en la base de datos
            cedula = form.cleaned_data.get('cedula')
            telefono = form.cleaned_data.get('telefono')
            
            # Crear perfil con el rol seleccionado
            perfil = Perfil.objects.create(
                usuario=usuario,
                cedula=cedula,
                telefono=telefono,
                rol=rol_seleccionado
            )
            
            # Asignar is_staff a roles con privilegios
            if rol_seleccionado in ['bodeguero', 'bibliotecario', 'admin', 'superusuario']:
                usuario.is_staff = True
                usuario.save()
            
            login(request, usuario)
            return redirect('index')
    else:
        form = RegistroUsuarioForm() 
    return render(request, 'gestion/templates/registration/registro.html', {'form': form})

def detalle_prestamo(request, id):
    prestamo = get_object_or_404(Prestamo, id=id)
    multas = prestamo.multas.all()
    return render(request, 'gestion/templates/detalle_prestamo.html', {
        'prestamo': prestamo,
        'multas': multas
    })

@requiere_rol('bibliotecario', 'admin')
def crear_multa(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        monto = request.POST.get('monto', 0)
        if tipo:
            multa = Multa.objects.create(
                prestamo=prestamo,
                tipo=tipo,
                monto=monto
            )
            return redirect('detalle_prestamo', id=prestamo.id)
    return render(request, 'gestion/templates/crear_multa.html', {'prestamo': prestamo})

@requiere_rol('bibliotecario', 'admin')
def devolver_libro(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    if request.method == 'POST':
        estado_libro = request.POST.get('estado_libro')

        # Marcar fecha de devolución
        prestamo.fecha_devolucion = timezone.now().date()
        prestamo.libro.disponible = True
        prestamo.libro.save()
        prestamo.save()
        
        # Crear multa por retraso si hay días de retraso
        if prestamo.dias_retraso > 0:
            Multa.objects.create(
                prestamo=prestamo,
                tipo='r',
                monto=prestamo.multa_retraso
            )
        
        # Crear multa por estado del libro
        if estado_libro == 'deterioro':
            Multa.objects.create(prestamo=prestamo, tipo='d', monto=10.00)
        elif estado_libro == 'perdida':
            Multa.objects.create(prestamo=prestamo, tipo='p', monto=20.00)
        
        return redirect('detalle_prestamo', id=prestamo.id)
    
    return redirect('detalle_prestamo', id=prestamo.id)

@requiere_rol('bibliotecario', 'admin')
def pagar_multa(request, multa_id):
    multa = get_object_or_404(Multa, id=multa_id)
    multa.pagada = True
    multa.save()
    
    return redirect('detalle_prestamo', id=multa.prestamo.id)

@requiere_rol('bibliotecario', 'admin')
def renovar_prestamo(request, prestamo_id):
    
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)
    
    from datetime import timedelta
    prestamo.fecha_max = timezone.now().date() + timedelta(days=7)
    prestamo.save()
    
    return redirect('detalle_prestamo', id=prestamo.id)

#API OPENLIBRARY
def api_buscar_libros(request):
    query = request.GET.get('q', '')
    if query:
        resultados = buscar_libros(query)

        # reiniciar los resultados
        libros = []
        for libro in resultados:
            libros.append({
                'titulo': libro.get('title', 'Sin título'),
                'autor': ', '.join(libro.get('author_name', ['Desconocido'])),
                'año': libro.get('first_publish_year', 'N/A'),
                'portada': f"https://covers.openlibrary.org/b/id/{libro.get('cover_i', '')}-M.jpg" if libro.get('cover_i') else None
            })
        return JsonResponse({'libros': libros})
    return JsonResponse({'libros': []})

def api_buscar_autores(request):
    query = request.GET.get('q', '')
    if query:
        resultados = buscar_autores(query)
        autores = []
        for autor in resultados:
            autores.append({
                'nombre': autor.get('name', 'Sin nombre'),
                'obras': autor.get('work_count', 0),
            })
        return JsonResponse({'autores': autores})
    return JsonResponse({'autores': []})

# Create your views here.

# usar el permission_required para proteger las vistas

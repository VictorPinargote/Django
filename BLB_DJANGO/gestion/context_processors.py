# Context processor para permisos de usuario
# Este archivo agrega variables de permisos al contexto de todos los templates

def permisos_usuario(request):
    """
    Agrega variables de permisos basadas en el rol del usuario.
    Esto evita tener condiciones largas en los templates.
    """
    permisos = {
        'puede_ver_autores': False,
        'puede_ver_prestamos': False,
        'puede_ver_multas': False,
        'puede_ver_solicitudes': False,
        'puede_gestionar_solicitudes': False,
        'puede_ver_usuarios': False,
        'puede_ver_logs': False,
        'rol_usuario': 'visitante',
        'rol_display': 'Visitante',
    }
    
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            rol = perfil.rol
            permisos['rol_usuario'] = rol
            permisos['rol_display'] = perfil.get_rol_display()
            
            # Usuario normal: puede ver sus préstamos, sus multas y solicitar
            if rol == 'usuario':
                permisos['puede_ver_prestamos'] = True
                permisos['puede_ver_multas'] = True
                permisos['puede_ver_solicitudes'] = True
            
            # Bodeguero: solo libros y autores
            elif rol == 'bodeguero':
                permisos['puede_ver_autores'] = True
            
            # Bibliotecario: préstamos, multas, solicitudes
            elif rol == 'bibliotecario':
                permisos['puede_ver_prestamos'] = True
                permisos['puede_ver_multas'] = True
                permisos['puede_ver_solicitudes'] = True
                permisos['puede_gestionar_solicitudes'] = True
            
            # Admin: todo excepto crear libros
            elif rol == 'admin':
                permisos['puede_ver_autores'] = True
                permisos['puede_ver_prestamos'] = True
                permisos['puede_ver_multas'] = True
                permisos['puede_ver_solicitudes'] = True
                permisos['puede_gestionar_solicitudes'] = True
                permisos['puede_ver_usuarios'] = True
                permisos['puede_ver_logs'] = True
            
            # Superusuario: acceso total
            elif rol == 'superusuario':
                permisos['puede_ver_autores'] = True
                permisos['puede_ver_prestamos'] = True
                permisos['puede_ver_multas'] = True
                permisos['puede_ver_solicitudes'] = True
                permisos['puede_gestionar_solicitudes'] = True
                permisos['puede_ver_usuarios'] = True
                permisos['puede_ver_logs'] = True
                
        except:
            # Si no tiene perfil, tratar como usuario normal
            permisos['puede_ver_prestamos'] = True
            permisos['puede_ver_solicitudes'] = True
    
    return permisos

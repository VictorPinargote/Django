def detalle_autor(request, id):
    """Vista pública para ver detalles de un autor"""
    autor = get_object_or_404(Autor, id=id)
    libros = Libro.objects.filter(autor=autor)
    
    # Check permissions logic
    puede_gestionar = False
    if request.user.is_authenticated:
        rol = obtener_rol(request.user)
        puede_gestionar = rol in ['bodeguero', 'superusuario']
        
    return render(request, 'gestion/templates/detalle_autor.html', {
        'autor': autor,
        'libros': libros,
        'puede_gestionar': puede_gestionar
    })

from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Autor)  #para ver los autores en la pagina de adminstracion, es necesario importar el objeto o modulo tambien con 
admin.site.register(Prestamo) #asi podemos ver los prestamos en la pagina de administracion, pero no podemos ver los detalles del prestamo
admin.site.register(Libro)
admin.site.register(Multa)
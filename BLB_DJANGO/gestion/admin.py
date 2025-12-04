from django.contrib import admin
from .models import Autor, Libro, Prestamo, multa
# Register your models here.

admin.site.register(Autor)  #paraa ver los autores en la pagina de adminstracion, es necesario importar el obketo o modulo tambien con
#from .models import Autor
admin.site.register(Prestamo)  #paraa ver los autores en la pagina de adminstracion, es necesario importar el obketo o modulo tambien con
#from .models import Autor
admin.site.register(Libro)  #paraa ver los autores en la pagina de adminstracion, es necesario importar el obketo o modulo tambien con
#from .models import libro
admin.site.register(multa)  #paraa ver los autores en la pagina de adminstracion, es necesario importar el obketo o modulo tambien con
#from .models import multa
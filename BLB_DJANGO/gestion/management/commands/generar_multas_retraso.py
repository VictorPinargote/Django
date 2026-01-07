"""
Comando de Django para generar multas automáticas por retraso.
Ejecutar con: python manage.py generar_multas_retraso

Para automatizar con cron (Linux/Mac):
0 8 * * * cd /ruta/proyecto && python manage.py generar_multas_retraso

Para Windows Task Scheduler:
Crear una tarea que ejecute: python manage.py generar_multas_retraso
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from gestion.models import Prestamo, Multa


class Command(BaseCommand):
    help = 'Genera multas automáticas por retraso y envía notificaciones por correo'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        
        # Buscar préstamos que:
        # 1. No han sido devueltos (fecha_devolucion es NULL)
        # 2. La fecha máxima ya pasó (están en retraso)
        prestamos_retrasados = Prestamo.objects.filter(
            fecha_devolucion__isnull=True,
            fecha_max__lt=hoy
        )
        
        multas_creadas = 0
        correos_enviados = 0
        
        for prestamo in prestamos_retrasados:
            # Verificar si ya existe una multa por retraso para este préstamo hoy
            multa_existente = Multa.objects.filter(
                prestamo=prestamo,
                tipo='r',
                fecha=hoy
            ).exists()
            
            if not multa_existente:
                # Calcular el monto de la multa (días de retraso * $2)
                dias_retraso = (hoy - prestamo.fecha_max).days
                monto = dias_retraso * 2.00
                
                # Crear la multa
                Multa.objects.create(
                    prestamo=prestamo,
                    tipo='r',
                    monto=monto
                )
                multas_creadas += 1
                
                # Intentar enviar correo al usuario
                usuario = prestamo.usuario
                if usuario.email:
                    try:
                        send_mail(
                            subject='📚 Notificación de Multa - BiblioTech',
                            message=f'''
Hola {usuario.first_name or usuario.username},

Te notificamos que tienes una multa pendiente por retraso en la devolución del libro:

📖 Libro: {prestamo.libro.titulo}
📅 Fecha máxima de devolución: {prestamo.fecha_max}
⏰ Días de retraso: {dias_retraso}
💰 Monto de la multa: ${monto:.2f}

Por favor, devuelve el libro lo antes posible para evitar que la multa siga aumentando.

Saludos,
El equipo de BiblioTech
                            ''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[usuario.email],
                            fail_silently=True,
                        )
                        correos_enviados += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error enviando correo a {usuario.email}: {str(e)}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Multas creadas: {multas_creadas}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📧 Correos enviados: {correos_enviados}')
        )

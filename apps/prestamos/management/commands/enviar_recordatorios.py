from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from prestamos.models import Prestamo

class Command(BaseCommand):
    help = 'Envía correos electrónicos de recordatorio de devolución (24h antes) y alertas de mora a lectores.'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        manana = hoy + timedelta(days=1)

        # 1. Recordatorio 24 horas antes del vencimiento
        prestamos_proximos = Prestamo.objects.filter(
            estado='Activo',
            fecha_limite=manana
        ).select_related('lector__user', 'libro')

        cont_recordatorios = 0
        for p in prestamos_proximos:
            email_lector = p.lector.user.email
            if email_lector:
                asunto = f"⏰ Recordatorio de Devolución: {p.libro.titulo}"
                mensaje = (
                    f"Hola {p.lector.user.get_full_name() or p.lector.user.username},\n\n"
                    f"Te recordamos que la fecha límite para devolver el libro '{p.libro.titulo}' "
                    f"vence mañana ({manana.strftime('%d/%m/%Y')}).\n\n"
                    f"Por favor acércate a la biblioteca para evitar sanciones en tu cuenta.\n\n"
                    f"Atentamente,\nBiblioteca Institucional"
                )
                try:
                    send_mail(asunto, mensaje, None, [email_lector], fail_silently=False)
                    cont_recordatorios += 1
                except Exception as e:
                    self.stderr.write(f"Error enviando correo a {email_lector}: {e}")

        # 2. Alertas de infracción por préstamos vencidos
        prestamos_vencidos = Prestamo.objects.filter(
            estado__in=['Activo', 'Atrasado'],
            fecha_limite__lt=hoy
        ).select_related('lector__user', 'libro')

        cont_alertas = 0
        for p in prestamos_vencidos:
            p.estado = 'Atrasado'
            p.dias_retraso = (hoy - p.fecha_limite).days
            p.lector.estado = 'Sancionado'
            p.lector.save()
            p.save()

            email_lector = p.lector.user.email
            if email_lector:
                asunto = f"⚠️ ALERTA DE INFRACCIÓN: Préstamo Atrasado - {p.libro.titulo}"
                mensaje = (
                    f"Estimado(a) {p.lector.user.get_full_name() or p.lector.user.username},\n\n"
                    f"Tu préstamo del libro '{p.libro.titulo}' presenta un retraso de {p.dias_retraso} día(s) "
                    f"(Fecha límite: {p.fecha_limite.strftime('%d/%m/%Y')}).\n\n"
                    f"Tu cuenta ha sido temporalmente SANCCIONADA. Te solicitamos devolver el ejemplar inmediatamente "
                    f"para regularizar tu situación.\n\n"
                    f"Atentamente,\nDirección de Biblioteca Institucional"
                )
                try:
                    send_mail(asunto, mensaje, None, [email_lector], fail_silently=False)
                    cont_alertas += 1
                except Exception as e:
                    self.stderr.write(f"Error enviando alerta a {email_lector}: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Proceso finalizado con éxito.\n"
            f"- Recordatorios (24h antes) enviados: {cont_recordatorios}\n"
            f"- Alertas de infracción enviadas: {cont_alertas}"
        ))

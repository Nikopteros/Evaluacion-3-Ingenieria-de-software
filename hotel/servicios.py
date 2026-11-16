"""
Servicios del Back End (ver diagrama de componentes):

  - DisponibilidadServicio  → qué habitaciones están libres en un rango de fechas.
  - ReservaServicio         → crear, confirmar, cancelar, check-in y check-out.
  - NotificacionServicio    → envía correos al huésped a través del servidor SMTP.

Las vistas llaman a estos servicios en vez de modificar los modelos directamente,
así las reglas de negocio quedan en un solo lugar.
"""
import logging

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Habitacion, Reserva

logger = logging.getLogger(__name__)


class ReglaNegocioError(Exception):
    """Error que se muestra al usuario (ej: check-in antes de la fecha de llegada)."""


def formato_clp(valor):
    try:
        return '$' + f'{int(valor):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return valor


# ---------------------------------------------------------------------------
class DisponibilidadServicio:
    @staticmethod
    def habitaciones_disponibles(entrada, salida, personas=1, tipo=None):
        """
        Habitaciones libres entre `entrada` y `salida` con capacidad suficiente.
        Se excluyen las que tienen una reserva activa que se cruza con esas fechas
        y las que están en mantención.
        """
        ocupadas = (
            Reserva.objects.activas().que_se_cruzan(entrada, salida).values('habitacion_id')
        )
        habitaciones = (
            Habitacion.objects.select_related('tipo')
            .exclude(estado=Habitacion.Estado.MANTENCION)
            .exclude(id__in=ocupadas)
            .filter(tipo__capacidad__gte=personas)
        )
        if tipo:
            habitaciones = habitaciones.filter(tipo=tipo)
        return habitaciones.order_by('tipo__precio_noche', 'numero')


# ---------------------------------------------------------------------------
class NotificacionServicio:
    @staticmethod
    def _detalle(reserva):
        return (
            f'Código de reserva: {reserva.codigo}\n'
            f'Habitación: {reserva.habitacion.numero} ({reserva.habitacion.tipo.nombre})\n'
            f'Llegada: {reserva.fecha_entrada:%d-%m-%Y}\n'
            f'Salida: {reserva.fecha_salida:%d-%m-%Y}\n'
            f'Noches: {reserva.noches}\n'
            f'Total estimado: {formato_clp(reserva.total)}\n'
        )

    @classmethod
    def _enviar(cls, reserva, asunto, introduccion):
        correo = reserva.huesped.correo
        if not correo:
            return
        cuerpo = (
            f'Hola {reserva.huesped.nombres}:\n\n{introduccion}\n\n{cls._detalle(reserva)}\n'
            'Saludos,\nHotel Ríos del Sur'
        )
        try:
            send_mail(f'Hotel Ríos del Sur · {asunto}', cuerpo, None, [correo])
        except Exception:  # un fallo del correo no debe impedir la operación
            logger.exception('No se pudo enviar el correo de la reserva %s', reserva.codigo)

    @classmethod
    def reserva_recibida(cls, reserva):
        cls._enviar(reserva, 'Solicitud de reserva recibida',
                    'Recibimos tu solicitud de reserva. Recepción la revisará y te avisaremos '
                    'cuando quede confirmada.')

    @classmethod
    def reserva_confirmada(cls, reserva):
        cls._enviar(reserva, 'Reserva confirmada', 'Tu reserva está confirmada. ¡Te esperamos!')

    @classmethod
    def reserva_cancelada(cls, reserva):
        cls._enviar(reserva, 'Reserva cancelada', 'Tu reserva fue cancelada.')


# ---------------------------------------------------------------------------
class ReservaServicio:
    @staticmethod
    @transaction.atomic
    def crear(reserva, usuario=None):
        """
        Guarda una reserva nueva. Se bloquea la fila de la habitación mientras se
        valida, para que dos personas no puedan reservarla al mismo tiempo.
        """
        Habitacion.objects.select_for_update().get(pk=reserva.habitacion_id)
        reserva.precio_noche = reserva.habitacion.tipo.precio_noche
        if usuario is not None and usuario.is_authenticated:
            reserva.creada_por = usuario
        reserva.full_clean()  # vuelve a revisar choques de fechas con la fila bloqueada
        reserva.save()

        if reserva.estado == Reserva.Estado.CONFIRMADA:
            transaction.on_commit(lambda: NotificacionServicio.reserva_confirmada(reserva))
        else:
            transaction.on_commit(lambda: NotificacionServicio.reserva_recibida(reserva))
        return reserva

    @staticmethod
    @transaction.atomic
    def confirmar(reserva):
        reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
        if reserva.estado != Reserva.Estado.PENDIENTE:
            raise ReglaNegocioError('Solo se pueden confirmar reservas pendientes.')
        if reserva.fecha_salida <= timezone.localdate():
            raise ReglaNegocioError('La fecha de salida de esta reserva ya pasó; no se puede confirmar.')
        reserva.estado = Reserva.Estado.CONFIRMADA
        reserva.save(update_fields=['estado'])
        transaction.on_commit(lambda: NotificacionServicio.reserva_confirmada(reserva))
        return f'Reserva {reserva.codigo} confirmada. Se notificó al huésped por correo.'

    @staticmethod
    @transaction.atomic
    def cancelar(reserva):
        reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
        if not reserva.puede_cancelarse:
            raise ReglaNegocioError(
                f'No se puede cancelar una reserva en estado "{reserva.get_estado_display()}".'
            )
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.cancelada_en = timezone.now()
        reserva.save(update_fields=['estado', 'cancelada_en'])
        transaction.on_commit(lambda: NotificacionServicio.reserva_cancelada(reserva))
        return f'Reserva {reserva.codigo} cancelada. La habitación quedó libre para esas fechas.'

    @staticmethod
    @transaction.atomic
    def check_in(reserva):
        reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
        hoy = timezone.localdate()
        if reserva.estado == Reserva.Estado.PENDIENTE:
            raise ReglaNegocioError('La reserva está pendiente. Confírmala antes de registrar el check-in.')
        if reserva.estado != Reserva.Estado.CONFIRMADA:
            raise ReglaNegocioError(
                f'No se puede hacer check-in de una reserva en estado "{reserva.get_estado_display()}".'
            )
        if hoy < reserva.fecha_entrada:
            raise ReglaNegocioError(
                f'El check-in de esta reserva está disponible desde el {reserva.fecha_entrada:%d-%m-%Y}.'
            )
        if hoy >= reserva.fecha_salida:
            raise ReglaNegocioError('La fecha de salida de esta reserva ya pasó.')

        habitacion = Habitacion.objects.select_for_update().get(pk=reserva.habitacion_id)
        if habitacion.estado != Habitacion.Estado.DISPONIBLE:
            raise ReglaNegocioError(
                f'La habitación {habitacion.numero} está "{habitacion.get_estado_display()}". '
                'Cambia su estado a Disponible antes de hacer el check-in.'
            )

        reserva.estado = Reserva.Estado.EN_CURSO
        reserva.checkin_en = timezone.now()
        reserva.save(update_fields=['estado', 'checkin_en'])
        habitacion.estado = Habitacion.Estado.OCUPADA
        habitacion.save(update_fields=['estado'])
        return (f'Check-in registrado: {reserva.huesped.nombre_completo} '
                f'en la habitación {habitacion.numero}.')

    @staticmethod
    @transaction.atomic
    def check_out(reserva):
        reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
        if reserva.estado != Reserva.Estado.EN_CURSO:
            raise ReglaNegocioError('Solo se puede hacer check-out de una reserva con check-in registrado.')

        reserva.estado = Reserva.Estado.FINALIZADA
        reserva.checkout_en = timezone.now()
        reserva.save(update_fields=['estado', 'checkout_en'])
        habitacion = Habitacion.objects.select_for_update().get(pk=reserva.habitacion_id)
        habitacion.estado = Habitacion.Estado.LIMPIEZA
        habitacion.save(update_fields=['estado'])
        return (f'Check-out registrado. Total de la estadía: {formato_clp(reserva.total)} '
                f'({reserva.noches} noche{"s" if reserva.noches != 1 else ""}). '
                f'La habitación {habitacion.numero} quedó en limpieza.')

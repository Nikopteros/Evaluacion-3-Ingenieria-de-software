from django import template

from ..servicios import formato_clp

register = template.Library()

COLORES_ESTADO = {
    # Habitaciones
    'disponible': 'success',
    'ocupada': 'danger',
    'limpieza': 'warning',
    'mantencion': 'secondary',
    # Reservas
    'pendiente': 'warning',
    'confirmada': 'primary',
    'en_curso': 'info',
    'finalizada': 'secondary',
    'cancelada': 'dark',
}


@register.filter
def clp(valor):
    """Formatea un número como pesos chilenos: 65000 → $65.000"""
    return formato_clp(valor)


@register.filter
def color_estado(estado):
    """Color de Bootstrap para el estado de una habitación o reserva."""
    return COLORES_ESTADO.get(estado, 'secondary')

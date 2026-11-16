import re

from django.core.exceptions import ValidationError


def normalizar_rut(rut):
    """Deja el RUT en formato 12345678-5 (sin puntos, con guion y K mayúscula)."""
    rut = (rut or '').replace('.', '').replace(' ', '').strip().upper()
    if '-' not in rut and len(rut) > 1:
        rut = f'{rut[:-1]}-{rut[-1]}'
    return rut


def calcular_dv(cuerpo):
    """Calcula el dígito verificador de un RUT chileno (algoritmo módulo 11)."""
    suma, multiplo = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def validar_rut(valor):
    rut = normalizar_rut(valor)
    if not re.fullmatch(r'\d{7,8}-[\dK]', rut):
        raise ValidationError('Formato de RUT inválido. Ejemplo: 12.345.678-5')
    cuerpo, dv = rut.split('-')
    if calcular_dv(cuerpo) != dv:
        raise ValidationError('El RUT no es válido (dígito verificador incorrecto).')


def validar_telefono(valor):
    """
    Acepta dígitos con un + opcional al inicio, espacios, guiones y paréntesis
    (ej: +56 9 1234 5678). Exige entre 8 y 15 dígitos en total.
    """
    valor = (valor or '').strip()
    if not valor:
        return
    if not re.fullmatch(r'\+?[\d\s\-()]+', valor):
        raise ValidationError(
            'El teléfono solo puede tener números, espacios, guiones y un + al inicio. '
            'Ejemplo: +56 9 1234 5678')
    digitos = re.sub(r'\D', '', valor)
    if not 8 <= len(digitos) <= 15:
        raise ValidationError('El teléfono debe tener entre 8 y 15 dígitos.')


def validar_numero_habitacion(valor):
    """El número de habitación solo puede tener dígitos (ej: 101, 302)."""
    if not re.fullmatch(r'\d{1,10}', (valor or '').strip()):
        raise ValidationError('El número de habitación solo puede tener dígitos. Ejemplo: 101')

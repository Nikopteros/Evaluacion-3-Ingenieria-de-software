"""
Modelos del sistema (componente "Modelos" del diagrama de componentes):
Huespedes, Reservas, Habitaciones y TiposHabitacion.
"""
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .validators import (
    normalizar_rut, validar_numero_habitacion, validar_rut, validar_telefono,
)


def generar_codigo_reserva():
    """Código corto y legible que se entrega al huésped (ej: RS-4F9A2C1B)."""
    return f'RS-{secrets.token_hex(4).upper()}'


class TipoHabitacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField('descripción', blank=True)
    capacidad = models.PositiveSmallIntegerField(
        'capacidad (personas)', validators=[MinValueValidator(1)]
    )
    precio_noche = models.PositiveIntegerField(
        'precio por noche', help_text='Valor en pesos chilenos (CLP), sin puntos.'
    )

    class Meta:
        ordering = ['precio_noche', 'nombre']
        verbose_name = 'tipo de habitación'
        verbose_name_plural = 'tipos de habitación'

    def __str__(self):
        return f'{self.nombre} ({self.capacidad} pers.)'


class Habitacion(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        OCUPADA = 'ocupada', 'Ocupada'
        LIMPIEZA = 'limpieza', 'En limpieza'
        MANTENCION = 'mantencion', 'En mantención'

    numero = models.CharField(
        'número', max_length=10, unique=True, validators=[validar_numero_habitacion],
        help_text='Solo dígitos. Las centenas indican el piso (ej: 203 está en el piso 2).',
    )
    piso = models.PositiveSmallIntegerField(default=1)
    tipo = models.ForeignKey(
        TipoHabitacion, on_delete=models.PROTECT, related_name='habitaciones',
        verbose_name='tipo de habitación',
    )
    servicios = models.CharField(
        max_length=255, blank=True, help_text='Ej: Wi-Fi, TV, baño privado, vista al río'
    )
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.DISPONIBLE)

    class Meta:
        ordering = ['piso', 'numero']
        verbose_name = 'habitación'
        verbose_name_plural = 'habitaciones'

    def __str__(self):
        return f'Hab. {self.numero} · {self.tipo.nombre} (hasta {self.tipo.capacidad} pers.)'

    def clean(self):
        # Se quitan espacios y ceros a la izquierda ("0102" queda como "102").
        numero = (self.numero or '').strip()
        if not numero.isdigit():
            return  # el validador del campo ya informa el error
        self.numero = str(int(numero))
        piso_esperado = int(numero) // 100
        if self.piso is not None and self.piso != piso_esperado:
            raise ValidationError({
                'piso': f'La habitación {self.numero} corresponde al piso {piso_esperado}. '
                        'Revisa el número o el piso.'
            })

    @property
    def lista_servicios(self):
        return [s.strip() for s in self.servicios.split(',') if s.strip()]


class Huesped(models.Model):
    class TipoDocumento(models.TextChoices):
        RUT = 'rut', 'RUT'
        PASAPORTE = 'pasaporte', 'Pasaporte'

    # Si el huésped se registró en la web, queda vinculado a su cuenta de usuario.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='huesped', editable=False,
    )
    tipo_documento = models.CharField(
        'tipo de documento', max_length=10, choices=TipoDocumento.choices, default=TipoDocumento.RUT
    )
    numero_documento = models.CharField(
        'número de documento', max_length=20,
        help_text='RUT con guion (ej: 12.345.678-5) o número de pasaporte.',
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField('correo electrónico')
    telefono = models.CharField(
        'teléfono', max_length=20, blank=True, validators=[validar_telefono],
        help_text='Ej: +56 9 1234 5678',
    )



    class Nacionalidad(models.TextChoices):
        CHILENA = 'Chilena', 'Chilena'
        ARGENTINA = 'Argentina', 'Argentina'
        PERUANA = 'Peruana', 'Peruana'
        BRASILENA = 'Brasileña', 'Brasileña'
        URUGUAYA = 'Uruguaya', 'Uruguaya'
        BOLIVIANA = 'Boliviana', 'Boliviana'
        PARAGUAYA = 'Paraguaya', 'Paraguaya'
        COLOMBIANA = 'Colombiana', 'Colombiana'
        VENEZOLANA = 'Venezolana', 'Venezolana'
        ECUATORIANA = 'Ecuatoriana', 'Ecuatoriana'
        MEXICANA = 'Mexicana', 'Mexicana'
        ESTADOUNIDENSE = 'Estadounidense', 'Estadounidense'
        ESPANOLA = 'Española', 'Española'
        OTRA = 'Otra', 'Otra'


    nacionalidad = models.CharField(
        max_length=30,
        choices=Nacionalidad.choices,
        default=Nacionalidad.CHILENA,
        verbose_name='nacionalidad'
    )


    
    fecha_registro = models.DateTimeField('registrado el', auto_now_add=True)

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'huésped'
        verbose_name_plural = 'huéspedes'
        constraints = [
            models.UniqueConstraint(
                fields=['tipo_documento', 'numero_documento'], name='huesped_documento_unico'
            )
        ]

    def __str__(self):
        return f'{self.nombre_completo} ({self.numero_documento})'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    def clean(self):
        if not self.numero_documento:
            return
        if self.tipo_documento == self.TipoDocumento.RUT:
            try:
                validar_rut(self.numero_documento)
            except ValidationError as error:
                raise ValidationError({'numero_documento': error.messages})
            self.numero_documento = normalizar_rut(self.numero_documento)
        else:
            self.numero_documento = self.numero_documento.strip().upper()


class ReservaQuerySet(models.QuerySet):
    def activas(self):
        """Reservas que bloquean la habitación: pendientes, confirmadas o en curso."""
        return self.filter(estado__in=Reserva.ESTADOS_ACTIVOS)

    def que_se_cruzan(self, entrada, salida):
        """
        Reservas cuyo rango de fechas se superpone con [entrada, salida).
        El día de salida queda libre: una reserva que termina el 10 no choca
        con otra que empieza el 10.
        """
        return self.filter(fecha_entrada__lt=salida, fecha_salida__gt=entrada)


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de confirmación'
        CONFIRMADA = 'confirmada', 'Confirmada'
        EN_CURSO = 'en_curso', 'En curso (check-in)'
        FINALIZADA = 'finalizada', 'Finalizada (check-out)'
        CANCELADA = 'cancelada', 'Cancelada'

    ESTADOS_ACTIVOS = (Estado.PENDIENTE, Estado.CONFIRMADA, Estado.EN_CURSO)
    ESTADOS_CANCELABLES = (Estado.PENDIENTE, Estado.CONFIRMADA)

    codigo = models.CharField(
        'código', max_length=12, unique=True, default=generar_codigo_reserva, editable=False
    )
    huesped = models.ForeignKey(
        Huesped, on_delete=models.PROTECT, related_name='reservas', verbose_name='huésped'
    )
    habitacion = models.ForeignKey(
        Habitacion, on_delete=models.PROTECT, related_name='reservas', verbose_name='habitación'
    )
    fecha_entrada = models.DateField('fecha de llegada')
    fecha_salida = models.DateField('fecha de salida')
    cantidad_personas = models.PositiveSmallIntegerField(
        'cantidad de personas', default=1, validators=[MinValueValidator(1)]
    )
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    # Se guarda el precio al momento de reservar, así un cambio de tarifa no altera reservas hechas.
    precio_noche = models.PositiveIntegerField('precio por noche', default=0, editable=False)
    observaciones = models.TextField(blank=True)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='reservas_creadas', editable=False,
    )
    fecha_creacion = models.DateTimeField('creada el', auto_now_add=True)
    checkin_en = models.DateTimeField('check-in realizado', null=True, blank=True, editable=False)
    checkout_en = models.DateTimeField('check-out realizado', null=True, blank=True, editable=False)
    cancelada_en = models.DateTimeField('cancelada el', null=True, blank=True, editable=False)

    objects = ReservaQuerySet.as_manager()

    class Meta:
        ordering = ['-fecha_entrada', '-fecha_creacion']
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'

    def __str__(self):
        return f'{self.codigo} · {self.huesped.nombre_completo} · Hab. {self.habitacion.numero}'

    @property
    def noches(self):
        return (self.fecha_salida - self.fecha_entrada).days

    @property
    def total(self):
        return self.noches * self.precio_noche

    @property
    def puede_cancelarse(self):
        return self.estado in self.ESTADOS_CANCELABLES

    def reservas_que_chocan(self):
        """Otras reservas activas de la MISMA habitación con fechas superpuestas."""
        return (
            Reserva.objects.activas()
            .que_se_cruzan(self.fecha_entrada, self.fecha_salida)
            .filter(habitacion_id=self.habitacion_id)
            .exclude(pk=self.pk)
        )

    def duplicado_del_huesped(self):
        """Otra reserva activa del MISMO huésped en fechas superpuestas (posible duplicado)."""
        return (
            Reserva.objects.activas()
            .que_se_cruzan(self.fecha_entrada, self.fecha_salida)
            .filter(huesped_id=self.huesped_id)
            .exclude(pk=self.pk)
            .select_related('habitacion')
            .first()
        )

    def clean(self):
        errores = {}
        if self.fecha_entrada and self.fecha_salida and self.fecha_salida <= self.fecha_entrada:
            errores['fecha_salida'] = 'La fecha de salida debe ser posterior a la de llegada.'
        if self.habitacion_id and self.cantidad_personas:
            capacidad = self.habitacion.tipo.capacidad
            if self.cantidad_personas > capacidad:
                errores['cantidad_personas'] = (
                    f'La habitación {self.habitacion.numero} admite como máximo {capacidad} '
                    f'persona{"s" if capacidad > 1 else ""}.'
                )
        if errores:
            raise ValidationError(errores)

        # Regla principal: evitar reservas duplicadas sobre la misma habitación.
        if (self.habitacion_id and self.fecha_entrada and self.fecha_salida
                and self.estado in self.ESTADOS_ACTIVOS):
            choque = self.reservas_que_chocan().first()
            if choque:
                raise ValidationError(
                    f'La habitación {self.habitacion.numero} ya está reservada entre el '
                    f'{choque.fecha_entrada:%d-%m-%Y} y el {choque.fecha_salida:%d-%m-%Y}. '
                    'Elige otras fechas u otra habitación.'
                )

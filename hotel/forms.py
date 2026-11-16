from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Habitacion, Huesped, Reserva, TipoHabitacion
from .validators import normalizar_rut, validar_rut


class CampoFecha(forms.DateInput):
    """Selector de fecha nativo del navegador (no necesita JavaScript)."""
    input_type = 'date'

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, format='%Y-%m-%d')


class BootstrapMixin:
    """Agrega las clases CSS de Bootstrap a todos los campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                clase = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                clase = 'form-check-input'
            else:
                clase = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {clase}".strip()


# ---------------------------------------------------------------------------
# Habitaciones
# ---------------------------------------------------------------------------
class TipoHabitacionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = TipoHabitacion
        fields = ['nombre', 'descripcion', 'capacidad', 'precio_noche']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class HabitacionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'piso', 'tipo', 'servicios']

    def clean(self):
        datos = super().clean()
        if not self.instance.pk:
            return datos  # habitación nueva: no tiene reservas

        # Se compara con lo guardado en la base, no con lo que viene en el formulario.
        original = Habitacion.objects.select_related('tipo').get(pk=self.instance.pk)
        ocupada = (original.estado == Habitacion.Estado.OCUPADA
                   or original.reservas.filter(estado=Reserva.Estado.EN_CURSO).exists())
        if ocupada:
            for campo in ('numero', 'piso', 'tipo'):
                if campo in datos and datos[campo] != getattr(original, campo):
                    self.add_error(campo, 'No se puede cambiar mientras la habitación está ocupada. '
                                          'Registra primero el check-out.')

        # Un tipo con menos capacidad no puede dejar reservas activas con más personas.
        nuevo_tipo = datos.get('tipo')
        if nuevo_tipo and nuevo_tipo != original.tipo:
            excedida = (original.reservas.activas()
                        .filter(cantidad_personas__gt=nuevo_tipo.capacidad).first())
            if excedida:
                self.add_error('tipo', (
                    f'La reserva {excedida.codigo} es para {excedida.cantidad_personas} personas y el '
                    f'tipo {nuevo_tipo.nombre} admite {nuevo_tipo.capacidad}. Cámbiala de habitación '
                    'o cancélala antes de cambiar el tipo.'))
        return datos


class HabitacionEstadoForm(BootstrapMixin, forms.ModelForm):
    """Actualizar estado de habitación (caso de uso de Recepción)."""

    class Meta:
        model = Habitacion
        fields = ['estado']

    def clean_estado(self):
        nuevo = self.cleaned_data['estado']
        tiene_huesped = self.instance.reservas.filter(estado=Reserva.Estado.EN_CURSO).exists()
        if tiene_huesped and nuevo != Habitacion.Estado.OCUPADA:
            raise ValidationError('La habitación tiene un huésped alojado. Registra primero su check-out.')
        if not tiene_huesped and nuevo == Habitacion.Estado.OCUPADA:
            raise ValidationError('Una habitación queda ocupada solo al registrar un check-in.')
        return nuevo


# ---------------------------------------------------------------------------
# Huéspedes
# ---------------------------------------------------------------------------
class HuespedForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Huesped
        fields = ['tipo_documento', 'numero_documento', 'nombres', 'apellidos',
                  'correo', 'telefono', 'nacionalidad']

    def clean(self):
        datos = super().clean()
        tipo, numero = datos.get('tipo_documento'), datos.get('numero_documento')
        if not (tipo and numero):
            return datos
        if tipo == Huesped.TipoDocumento.RUT:
            try:
                validar_rut(numero)
            except ValidationError as error:
                self.add_error('numero_documento', error)
                return datos
            numero = normalizar_rut(numero)
        else:
            numero = numero.strip().upper()
        datos['numero_documento'] = numero

        # Evita registrar dos veces a la misma persona (problema de los registros manuales).
        if Huesped.objects.filter(tipo_documento=tipo, numero_documento=numero) \
                .exclude(pk=self.instance.pk).exists():
            self.add_error('numero_documento', 'Ya existe un huésped registrado con este documento.')
        return datos


class RegistroUsuarioForm(BootstrapMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)
        labels = {'username': 'Nombre de usuario'}


# ---------------------------------------------------------------------------
# Disponibilidad y reservas
# ---------------------------------------------------------------------------
class DisponibilidadForm(BootstrapMixin, forms.Form):
    fecha_entrada = forms.DateField(label='Llegada', widget=CampoFecha())
    fecha_salida = forms.DateField(label='Salida', widget=CampoFecha())
    personas = forms.IntegerField(label='Personas', min_value=1, max_value=10, initial=1)
    tipo = forms.ModelChoiceField(
        TipoHabitacion.objects.all(), required=False, empty_label='Cualquier tipo',
        label='Tipo de habitación',
    )

    def clean(self):
        datos = super().clean()
        entrada, salida = datos.get('fecha_entrada'), datos.get('fecha_salida')
        if entrada and entrada < timezone.localdate():
            self.add_error('fecha_entrada', 'La fecha de llegada no puede ser anterior a hoy.')
        if entrada and salida and salida <= entrada:
            self.add_error('fecha_salida', 'La salida debe ser posterior a la llegada.')
        return datos


class ReservaBaseForm(BootstrapMixin, forms.ModelForm):
    def clean_fecha_entrada(self):
        entrada = self.cleaned_data['fecha_entrada']
        if entrada < timezone.localdate():
            raise ValidationError('La fecha de llegada no puede ser anterior a hoy.')
        return entrada

    def _buscar_duplicado(self, huesped):
        entrada = self.cleaned_data.get('fecha_entrada')
        salida = self.cleaned_data.get('fecha_salida')
        if not (huesped and entrada and salida and salida > entrada):
            return None
        tentativa = Reserva(pk=self.instance.pk, huesped=huesped,
                            fecha_entrada=entrada, fecha_salida=salida)
        return tentativa.duplicado_del_huesped()



class ReservaClienteForm(ReservaBaseForm):
    """El cliente elige fechas; la cantidad de personas viene de disponibilidad."""

    class Meta:
        model = Reserva
        fields = ['fecha_entrada', 'fecha_salida', 'observaciones']
        widgets = {
            'fecha_entrada': CampoFecha(),
            'fecha_salida': CampoFecha(),
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ej: hora estimada de llegada, cama extra, etc.'
            }),
        }

    def clean(self):
        datos = super().clean()
        duplicado = self._buscar_duplicado(self.instance.huesped)

        if duplicado:
            raise ValidationError(
                f'Ya tienes la reserva {duplicado.codigo} '
                f'(habitación {duplicado.habitacion.numero}) '
                'en fechas que se cruzan con estas. Revisa "Mis reservas" '
                'antes de reservar de nuevo.'
            )

        return datos

class ReservaRecepcionForm(ReservaBaseForm):
    reserva_adicional = forms.BooleanField(
        required=False, label='Es una reserva adicional del mismo huésped (ej: grupo familiar)',
        help_text='Márcalo solo si el huésped realmente necesita otra habitación en esas fechas.',
    )

    class Meta:
        model = Reserva
        fields = ['huesped', 'habitacion', 'fecha_entrada', 'fecha_salida',
                  'cantidad_personas', 'observaciones']
        widgets = {
            'fecha_entrada': CampoFecha(),
            'fecha_salida': CampoFecha(),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['habitacion'].queryset = (
            Habitacion.objects.select_related('tipo').exclude(estado=Habitacion.Estado.MANTENCION)
        )

    def clean(self):
        datos = super().clean()
        duplicado = self._buscar_duplicado(datos.get('huesped'))
        if duplicado and not datos.get('reserva_adicional'):
            self.add_error(
                'reserva_adicional',
                f'Este huésped ya tiene la reserva {duplicado.codigo} (habitación '
                f'{duplicado.habitacion.numero}) en esas fechas. Si no es un duplicado, marca esta opción.'
            )
        return datos

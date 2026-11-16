"""
Vistas (Controllers) del sistema. Se agrupan por actor del diagrama de casos de uso:
Invitado (público), Cliente y Recepción.
"""
from datetime import date
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from .forms import (
    DisponibilidadForm, HabitacionEstadoForm, HabitacionForm, HuespedForm, RegistroUsuarioForm,
    ReservaClienteForm, ReservaRecepcionForm, TipoHabitacionForm,
)
from .mixins import (
    GRUPO_CLIENTE, ClienteRequeridoMixin, RecepcionRequeridaMixin, es_cliente, es_recepcion,
)
from .models import Habitacion, Huesped, Reserva, TipoHabitacion
from .servicios import DisponibilidadServicio, ReglaNegocioError, ReservaServicio
from .validators import normalizar_rut


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def agregar_errores(form, error):
    """Pasa un ValidationError del modelo/servicio al formulario."""
    if hasattr(error, 'error_dict'):
        for campo, errores in error.error_dict.items():
            form.add_error(campo if campo in form.fields else None, errores)
    else:
        form.add_error(None, error)


def con_huesped_actual(habitaciones):
    """Agrega a cada habitación su reserva en curso (huésped alojado), si tiene."""
    habitaciones = list(habitaciones)
    en_curso = {
        r.habitacion_id: r
        for r in Reserva.objects.filter(estado=Reserva.Estado.EN_CURSO).select_related('huesped')
    }
    for habitacion in habitaciones:
        habitacion.reserva_en_curso = en_curso.get(habitacion.pk)
    return habitaciones


class FiltrosMixin:
    """Conserva los filtros de búsqueda al cambiar de página."""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        ctx['filtros'] = parametros.urlencode()
        return ctx


class FormularioMixin(SuccessMessageMixin):
    """Formulario genérico con título y botón volver."""
    template_name = 'hotel/form_generico.html'
    titulo = ''
    volver = None

    def get_subtitulo(self):
        return ''

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titulo=self.titulo, subtitulo=self.get_subtitulo(), volver_url=reverse(self.volver))
        return ctx


# ---------------------------------------------------------------------------
# Público (Invitado): ver habitaciones, consultar disponibilidad, registrarse
# ---------------------------------------------------------------------------
def inicio(request):
    tipos = TipoHabitacion.objects.annotate(total=Count('habitaciones')).order_by('precio_noche', 'nombre')
    return render(request, 'hotel/inicio.html', {'tipos': tipos, 'form': DisponibilidadForm()})


def catalogo(request):
    tipos = TipoHabitacion.objects.prefetch_related('habitaciones')
    return render(request, 'hotel/catalogo.html', {'tipos': tipos})


def consultar_disponibilidad(request):
    form = DisponibilidadForm(request.GET or None)
    resultados, noches, qs_reserva = None, 0, ''
    if form.is_valid():
        datos = form.cleaned_data
        entrada, salida = datos['fecha_entrada'], datos['fecha_salida']
        noches = (salida - entrada).days
        resultados = list(DisponibilidadServicio.habitaciones_disponibles(
            entrada, salida, datos['personas'], datos.get('tipo')))
        for habitacion in resultados:
            habitacion.total_estadia = noches * habitacion.tipo.precio_noche
        qs_reserva = urlencode({
            'fecha_entrada': entrada.isoformat(),
            'fecha_salida': salida.isoformat(),
            'cantidad_personas': datos['personas'],
        })
    return render(request, 'hotel/disponibilidad.html', {
        'form': form, 'resultados': resultados, 'noches': noches, 'qs_reserva': qs_reserva,
    })


def _huesped_sin_cuenta(datos, prefijo):
    """
    Si la persona ya fue registrada por recepción (ej: reservó por teléfono) y aún no
    tiene cuenta web, se reutiliza su ficha en vez de crear un huésped duplicado.
    Se exige que el correo coincida con el registrado.
    """
    tipo = datos.get(f'{prefijo}-tipo_documento')
    numero = (datos.get(f'{prefijo}-numero_documento') or '').strip()
    correo = (datos.get(f'{prefijo}-correo') or '').strip()
    if not (tipo and numero and correo):
        return None
    numero = normalizar_rut(numero) if tipo == Huesped.TipoDocumento.RUT else numero.upper()
    return Huesped.objects.filter(
        tipo_documento=tipo, numero_documento=numero, usuario__isnull=True, correo__iexact=correo,
    ).first()


def registro(request):
    if request.user.is_authenticated:
        return redirect('hotel:redireccion')

    existente = _huesped_sin_cuenta(request.POST, 'h') if request.method == 'POST' else None
    usuario_form = RegistroUsuarioForm(request.POST or None, prefix='u')
    huesped_form = HuespedForm(request.POST or None, prefix='h', instance=existente)

    if request.method == 'POST':
        validos = [usuario_form.is_valid(), huesped_form.is_valid()]  # valida ambos
        if all(validos):
            with transaction.atomic():
                huesped = huesped_form.save(commit=False)
                usuario = usuario_form.save(commit=False)
                usuario.email = huesped.correo
                usuario.first_name = huesped.nombres[:150]
                usuario.last_name = huesped.apellidos[:150]
                usuario.save()
                usuario.groups.add(Group.objects.get_or_create(name=GRUPO_CLIENTE)[0])
                huesped.usuario = usuario
                huesped.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenido/a, {huesped.nombres}! Ya puedes hacer tus reservas.')
            return redirect('hotel:disponibilidad')

    return render(request, 'hotel/registro.html', {
        'usuario_form': usuario_form, 'huesped_form': huesped_form,
    })


@login_required
def redireccion(request):
    """Después del login, cada rol va a su pantalla principal."""
    if es_recepcion(request.user):
        return redirect('hotel:panel')
    if es_cliente(request.user):
        return redirect('hotel:mis_reservas')
    return redirect('hotel:inicio')


# ---------------------------------------------------------------------------
# Cliente: realizar reserva, consultar y cancelar sus reservas
# ---------------------------------------------------------------------------
class MisReservasView(ClienteRequeridoMixin, ListView):
    template_name = 'hotel/mis_reservas.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        return self.request.user.huesped.reservas.select_related('habitacion__tipo')


class ReservaClienteCreateView(ClienteRequeridoMixin, CreateView):
    model = Reserva
    form_class = ReservaClienteForm
    template_name = 'hotel/reserva_cliente_form.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.habitacion = get_object_or_404(
            Habitacion.objects.select_related('tipo'), pk=kwargs['habitacion_id'])

    def get_initial(self):
        inicial = super().get_initial()
        for campo in ('fecha_entrada', 'fecha_salida'):
            if self.request.GET.get(campo):
                inicial[campo] = self.request.GET[campo]
        return inicial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        try:
            cantidad = int(self.request.GET.get('cantidad_personas', 1))
        except (TypeError, ValueError):
            cantidad = 1

        kwargs['instance'] = Reserva(
            huesped=self.request.user.huesped, habitacion=self.habitacion,
            estado=Reserva.Estado.PENDIENTE,
            cantidad_personas=cantidad,
        )
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['habitacion'] = self.habitacion
        ctx['cantidad_personas'] = ctx['form'].instance.cantidad_personas
        return ctx

    def form_valid(self, form):
        try:
            reserva = ReservaServicio.crear(form.instance, usuario=self.request.user)
        except ValidationError as error:
            agregar_errores(form, error)
            return self.form_invalid(form)
        messages.success(
            self.request,
            f'Solicitud enviada. Tu código de reserva es {reserva.codigo}. '
            'Recepción la confirmará y te avisaremos por correo.')
        return redirect('hotel:mis_reservas')


class ClienteCancelarReservaView(ClienteRequeridoMixin, View):
    def _reserva(self, request, pk):
        return get_object_or_404(
            Reserva.objects.select_related('habitacion__tipo', 'huesped'),
            pk=pk, huesped=request.user.huesped)

    def get(self, request, pk):
        reserva = self._reserva(request, pk)
        if not reserva.puede_cancelarse:
            messages.error(request, 'Esta reserva ya no se puede cancelar.')
            return redirect('hotel:mis_reservas')
        return render(request, 'hotel/confirmar_accion.html', {
            'reserva': reserva, 'titulo': 'Cancelar reserva', 'color': 'danger',
            'descripcion': 'La habitación quedará libre para otros huéspedes. Esta acción no se puede deshacer.',
            'volver_url': reverse('hotel:mis_reservas'),
        })

    def post(self, request, pk):
        reserva = self._reserva(request, pk)
        try:
            messages.success(request, ReservaServicio.cancelar(reserva))
        except ReglaNegocioError as error:
            messages.error(request, str(error))
        return redirect('hotel:mis_reservas')


# ---------------------------------------------------------------------------
# Recepción: panel de ocupación
# ---------------------------------------------------------------------------
class PanelView(RecepcionRequeridaMixin, TemplateView):
    """Control de habitaciones ocupadas y disponibles + llegadas y salidas del día."""
    template_name = 'hotel/panel.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        habitaciones = con_huesped_actual(Habitacion.objects.select_related('tipo'))
        conteo = {estado: 0 for estado in Habitacion.Estado.values}
        for habitacion in habitaciones:
            conteo[habitacion.estado] += 1
        total = len(habitaciones)
        ocupadas = conteo[Habitacion.Estado.OCUPADA]

        ctx.update(
            hoy=hoy,
            habitaciones=habitaciones,
            total=total,
            indicadores=[(Habitacion.Estado(e).label, conteo[e], e) for e in Habitacion.Estado.values],
            porcentaje_ocupacion=round(ocupadas * 100 / total) if total else 0,
            llegadas=Reserva.objects.filter(
                fecha_entrada__lte=hoy, fecha_salida__gt=hoy,
                estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA],
            ).select_related('huesped', 'habitacion').order_by('fecha_entrada'),
            salidas=Reserva.objects.filter(
                estado=Reserva.Estado.EN_CURSO, fecha_salida__lte=hoy,
            ).select_related('huesped', 'habitacion'),
            pendientes=Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE).count(),
        )
        return ctx


# ---------------------------------------------------------------------------
# Recepción: registro y administración de habitaciones
# ---------------------------------------------------------------------------
class HabitacionListView(RecepcionRequeridaMixin, ListView):
    template_name = 'hotel/habitacion_lista.html'

    def get_queryset(self):
        qs = Habitacion.objects.select_related('tipo')
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['habitaciones'] = con_huesped_actual(ctx['object_list'])
        ctx['estados'] = Habitacion.Estado.choices
        ctx['estado_sel'] = self.request.GET.get('estado', '')
        return ctx


class HabitacionCreateView(RecepcionRequeridaMixin, FormularioMixin, CreateView):
    model = Habitacion
    form_class = HabitacionForm
    titulo = 'Registrar habitación'
    volver = 'hotel:habitacion_lista'
    success_url = reverse_lazy('hotel:habitacion_lista')
    success_message = 'Habitación %(numero)s registrada.'


class HabitacionUpdateView(RecepcionRequeridaMixin, FormularioMixin, UpdateView):
    model = Habitacion
    form_class = HabitacionForm
    titulo = 'Editar habitación'
    volver = 'hotel:habitacion_lista'
    success_url = reverse_lazy('hotel:habitacion_lista')
    success_message = 'Habitación %(numero)s actualizada.'


class HabitacionEstadoView(RecepcionRequeridaMixin, FormularioMixin, UpdateView):
    model = Habitacion
    form_class = HabitacionEstadoForm
    titulo = 'Actualizar estado de habitación'
    volver = 'hotel:habitacion_lista'
    success_url = reverse_lazy('hotel:habitacion_lista')

    def get_subtitulo(self):
        return str(self.object)

    def get_success_message(self, cleaned_data):
        return f'Habitación {self.object.numero}: estado cambiado a "{self.object.get_estado_display()}".'


class TipoListView(RecepcionRequeridaMixin, ListView):
    template_name = 'hotel/tipo_lista.html'
    context_object_name = 'tipos'

    def get_queryset(self):
        return TipoHabitacion.objects.annotate(total=Count('habitaciones')).order_by('precio_noche', 'nombre')


class TipoCreateView(RecepcionRequeridaMixin, FormularioMixin, CreateView):
    model = TipoHabitacion
    form_class = TipoHabitacionForm
    titulo = 'Nuevo tipo de habitación'
    volver = 'hotel:tipo_lista'
    success_url = reverse_lazy('hotel:tipo_lista')
    success_message = 'Tipo "%(nombre)s" creado.'


class TipoUpdateView(RecepcionRequeridaMixin, FormularioMixin, UpdateView):
    model = TipoHabitacion
    form_class = TipoHabitacionForm
    titulo = 'Editar tipo de habitación'
    volver = 'hotel:tipo_lista'
    success_url = reverse_lazy('hotel:tipo_lista')
    success_message = 'Tipo "%(nombre)s" actualizado.'

    def get_subtitulo(self):
        return 'El cambio de precio solo afecta a las reservas nuevas.'


# ---------------------------------------------------------------------------
# Recepción: registro de huéspedes
# ---------------------------------------------------------------------------
class HuespedListView(RecepcionRequeridaMixin, FiltrosMixin, ListView):
    template_name = 'hotel/huesped_lista.html'
    context_object_name = 'huespedes'
    paginate_by = 20

    def get_queryset(self):
        qs = Huesped.objects.annotate(total_reservas=Count('reservas')).order_by('apellidos', 'nombres')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(correo__icontains=q)
                | Q(numero_documento__icontains=q.replace('.', '').upper())
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class HuespedCreateView(RecepcionRequeridaMixin, FormularioMixin, CreateView):
    model = Huesped
    form_class = HuespedForm
    titulo = 'Registrar huésped'
    volver = 'hotel:huesped_lista'
    success_message = 'Huésped %(nombres)s %(apellidos)s registrado.'

    def get_success_url(self):
        return reverse('hotel:huesped_detalle', args=[self.object.pk])


class HuespedUpdateView(RecepcionRequeridaMixin, FormularioMixin, UpdateView):
    model = Huesped
    form_class = HuespedForm
    titulo = 'Editar huésped'
    volver = 'hotel:huesped_lista'
    success_message = 'Datos de %(nombres)s %(apellidos)s actualizados.'

    def get_success_url(self):
        return reverse('hotel:huesped_detalle', args=[self.object.pk])


class HuespedDetailView(RecepcionRequeridaMixin, DetailView):
    model = Huesped
    template_name = 'hotel/huesped_detalle.html'
    context_object_name = 'huesped'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reservas'] = self.object.reservas.select_related('habitacion__tipo')
        return ctx


# ---------------------------------------------------------------------------
# Recepción: creación, consulta y cancelación de reservas; check-in y check-out
# ---------------------------------------------------------------------------
class ReservaListView(RecepcionRequeridaMixin, FiltrosMixin, ListView):
    template_name = 'hotel/reserva_lista.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def get_queryset(self):
        qs = Reserva.objects.select_related('huesped', 'habitacion__tipo')
        estado = self.request.GET.get('estado')
        q = self.request.GET.get('q', '').strip()
        fecha = self.request.GET.get('fecha')
        if estado:
            qs = qs.filter(estado=estado)
        if q:
            qs = qs.filter(
                Q(codigo__icontains=q) | Q(huesped__nombres__icontains=q)
                | Q(huesped__apellidos__icontains=q) | Q(habitacion__numero=q)
                | Q(huesped__numero_documento__icontains=q.replace('.', '').upper())
            )
        if fecha:
            try:
                dia = date.fromisoformat(fecha)
                qs = qs.filter(fecha_entrada__lte=dia, fecha_salida__gt=dia)
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            estados=Reserva.Estado.choices,
            estado_sel=self.request.GET.get('estado', ''),
            q=self.request.GET.get('q', ''),
            fecha=self.request.GET.get('fecha', ''),
        )
        return ctx


class ReservaCreateView(RecepcionRequeridaMixin, FormularioMixin, CreateView):
    """Reserva tomada por recepción (ej: por teléfono). Queda confirmada de inmediato."""
    model = Reserva
    form_class = ReservaRecepcionForm
    titulo = 'Nueva reserva'
    volver = 'hotel:reserva_lista'

    def get_subtitulo(self):
        return 'Las reservas creadas por recepción quedan confirmadas de inmediato.'

    def get_initial(self):
        inicial = super().get_initial()
        for campo in ('huesped', 'habitacion', 'fecha_entrada', 'fecha_salida', 'cantidad_personas'):
            if self.request.GET.get(campo):
                inicial[campo] = self.request.GET[campo]
        return inicial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['enlace_extra'] = (reverse('hotel:huesped_nuevo'), '¿Huésped nuevo? Regístralo primero aquí')
        return ctx

    def form_valid(self, form):
        form.instance.estado = Reserva.Estado.CONFIRMADA
        try:
            reserva = ReservaServicio.crear(form.instance, usuario=self.request.user)
        except ValidationError as error:
            agregar_errores(form, error)
            return self.form_invalid(form)
        messages.success(self.request, f'Reserva {reserva.codigo} creada y confirmada.')
        return redirect('hotel:reserva_detalle', pk=reserva.pk)


class ReservaDetailView(RecepcionRequeridaMixin, DetailView):
    model = Reserva
    template_name = 'hotel/reserva_detalle.html'
    context_object_name = 'reserva'

    def get_queryset(self):
        return Reserva.objects.select_related('huesped', 'habitacion__tipo', 'creada_por')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hoy'] = timezone.localdate()
        return ctx


class AccionReservaView(RecepcionRequeridaMixin, View):
    """Confirmar, cancelar, check-in y check-out. GET pide confirmación, POST ejecuta."""
    accion = None
    ACCIONES = {
        'confirmar': ('Confirmar reserva', 'success', ReservaServicio.confirmar,
                      'La reserva quedará confirmada y se avisará al huésped por correo.'),
        'cancelar': ('Cancelar reserva', 'danger', ReservaServicio.cancelar,
                     'La habitación quedará libre para esas fechas. Esta acción no se puede deshacer.'),
        'checkin': ('Registrar check-in', 'primary', ReservaServicio.check_in,
                    'El huésped ingresa al hotel y la habitación pasa a estado Ocupada.'),
        'checkout': ('Registrar check-out', 'warning', ReservaServicio.check_out,
                     'El huésped deja el hotel y la habitación pasa a estado En limpieza.'),
    }

    def get(self, request, pk):
        reserva = get_object_or_404(
            Reserva.objects.select_related('huesped', 'habitacion__tipo'), pk=pk)
        titulo, color, _, descripcion = self.ACCIONES[self.accion]
        return render(request, 'hotel/confirmar_accion.html', {
            'reserva': reserva, 'titulo': titulo, 'color': color, 'descripcion': descripcion,
            'volver_url': reverse('hotel:reserva_detalle', args=[pk]),
        })

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        accion = self.ACCIONES[self.accion][2]
        try:
            messages.success(request, accion(reserva))
        except ReglaNegocioError as error:
            messages.error(request, str(error))
        return redirect('hotel:reserva_detalle', pk=pk)

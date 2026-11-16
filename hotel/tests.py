"""
Pruebas de las reglas de negocio principales.
Ejecutar con:  python manage.py test hotel
"""
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .mixins import GRUPO_RECEPCION
from .models import Habitacion, Huesped, Reserva, TipoHabitacion
from .forms import HabitacionForm
from .servicios import DisponibilidadServicio, ReglaNegocioError, ReservaServicio
from .validators import validar_rut, validar_telefono


class BaseHotelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hoy = timezone.localdate()
        cls.tipo = TipoHabitacion.objects.create(nombre='Doble', capacidad=2, precio_noche=50000)
        cls.hab = Habitacion.objects.create(numero='101', tipo=cls.tipo)
        cls.hab2 = Habitacion.objects.create(numero='102', tipo=cls.tipo)
        cls.huesped = Huesped.objects.create(
            tipo_documento='rut', numero_documento='12345678-5',
            nombres='Ana', apellidos='Soto', correo='ana@example.com')

    def reservar(self, desde, noches, habitacion=None, estado=Reserva.Estado.CONFIRMADA):
        entrada = self.hoy + timedelta(days=desde)
        reserva = Reserva(huesped=self.huesped, habitacion=habitacion or self.hab,
                          fecha_entrada=entrada, fecha_salida=entrada + timedelta(days=noches),
                          estado=estado)
        return ReservaServicio.crear(reserva)


class ReservasDuplicadasTest(BaseHotelTest):
    def test_no_permite_reservas_superpuestas_en_la_misma_habitacion(self):
        self.reservar(0, 3)
        with self.assertRaises(ValidationError):
            self.reservar(2, 2)

    def test_permite_reserva_que_empieza_el_dia_de_salida_de_otra(self):
        self.reservar(0, 3)
        self.reservar(3, 2)
        self.assertEqual(Reserva.objects.count(), 2)

    def test_reserva_cancelada_libera_la_habitacion(self):
        reserva = self.reservar(0, 3)
        ReservaServicio.cancelar(reserva)
        self.reservar(1, 1)
        self.assertEqual(Reserva.objects.activas().count(), 1)

    def test_no_permite_mas_personas_que_la_capacidad(self):
        reserva = Reserva(huesped=self.huesped, habitacion=self.hab, cantidad_personas=3,
                          fecha_entrada=self.hoy, fecha_salida=self.hoy + timedelta(days=1))
        with self.assertRaises(ValidationError):
            ReservaServicio.crear(reserva)

    def test_guarda_el_precio_y_calcula_el_total(self):
        reserva = self.reservar(0, 3)
        self.assertEqual(reserva.precio_noche, 50000)
        self.assertEqual(reserva.total, 150000)


class DisponibilidadTest(BaseHotelTest):
    def test_excluye_habitaciones_reservadas_y_en_mantencion(self):
        self.reservar(1, 2)  # ocupa la 101
        entrada, salida = self.hoy + timedelta(days=1), self.hoy + timedelta(days=3)
        libres = list(DisponibilidadServicio.habitaciones_disponibles(entrada, salida))
        self.assertEqual(libres, [self.hab2])

        self.hab2.estado = Habitacion.Estado.MANTENCION
        self.hab2.save()
        self.assertFalse(DisponibilidadServicio.habitaciones_disponibles(entrada, salida).exists())


class CheckInCheckOutTest(BaseHotelTest):
    def test_flujo_completo_actualiza_estado_de_la_habitacion(self):
        reserva = self.reservar(0, 2)
        ReservaServicio.check_in(reserva)
        self.hab.refresh_from_db()
        reserva.refresh_from_db()
        self.assertEqual(self.hab.estado, Habitacion.Estado.OCUPADA)
        self.assertEqual(reserva.estado, Reserva.Estado.EN_CURSO)

        ReservaServicio.check_out(reserva)
        self.hab.refresh_from_db()
        reserva.refresh_from_db()
        self.assertEqual(self.hab.estado, Habitacion.Estado.LIMPIEZA)
        self.assertEqual(reserva.estado, Reserva.Estado.FINALIZADA)

    def test_no_permite_check_in_de_reserva_pendiente(self):
        reserva = self.reservar(0, 2, estado=Reserva.Estado.PENDIENTE)
        with self.assertRaises(ReglaNegocioError):
            ReservaServicio.check_in(reserva)

    def test_no_permite_check_in_antes_de_la_fecha(self):
        reserva = self.reservar(5, 2)
        with self.assertRaises(ReglaNegocioError):
            ReservaServicio.check_in(reserva)


class HuespedTest(TestCase):
    def test_validacion_de_rut(self):
        validar_rut('12.345.678-5')
        validar_rut('11111111-1')
        with self.assertRaises(ValidationError):
            validar_rut('12345678-9')

    def test_telefono_debe_tener_numeros(self):
        validar_telefono('+56 9 1234 5678')
        validar_telefono('912345678')
        for malo in ('asfasfasf', '+56 9 abcd 5678', '123'):
            with self.assertRaises(ValidationError):
                validar_telefono(malo)

    def test_registro_web_reutiliza_huesped_registrado_por_recepcion(self):
        Huesped.objects.create(tipo_documento='rut', numero_documento='11111111-1',
                               nombres='María', apellidos='Rojas', correo='maria@example.com')
        respuesta = self.client.post(reverse('hotel:registro'), {
            'h-tipo_documento': 'rut', 'h-numero_documento': '11.111.111-1',
            'h-nombres': 'María', 'h-apellidos': 'Rojas', 'h-correo': 'maria@example.com',
            'h-telefono': '', 'h-nacionalidad': 'Chilena',
            'u-username': 'maria', 'u-password1': 'ClaveSegura2026!', 'u-password2': 'ClaveSegura2026!',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Huesped.objects.count(), 1)
        self.assertEqual(Huesped.objects.get().usuario.username, 'maria')


class PermisosTest(BaseHotelTest):
    def test_invitado_es_enviado_al_login(self):
        respuesta = self.client.get(reverse('hotel:panel'))
        self.assertEqual(respuesta.status_code, 302)

    def test_cliente_no_accede_a_recepcion(self):
        usuario = User.objects.create_user('cliente', password='x')
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse('hotel:panel')).status_code, 403)

    def test_recepcion_accede_al_panel(self):
        usuario = User.objects.create_user('recepcion', password='x')
        usuario.groups.add(Group.objects.create(name=GRUPO_RECEPCION))
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse('hotel:panel')).status_code, 200)


class HabitacionFormTest(BaseHotelTest):
    def datos(self, **cambios):
        datos = {'numero': '101', 'piso': 1, 'tipo': self.tipo.pk, 'servicios': 'Wi-Fi'}
        datos.update(cambios)
        return datos

    def test_numero_solo_digitos(self):
        form = HabitacionForm(self.datos(numero='adsasdasd'))
        self.assertFalse(form.is_valid())
        self.assertIn('numero', form.errors)

    def test_piso_debe_calzar_con_el_numero(self):
        form = HabitacionForm(self.datos(numero='205', piso=999))
        self.assertFalse(form.is_valid())
        self.assertIn('piso', form.errors)
        self.assertTrue(HabitacionForm(self.datos(numero='205', piso=2)).is_valid())

    def test_no_cambia_tipo_ni_piso_con_huesped_alojado(self):
        familiar = TipoHabitacion.objects.create(nombre='Familiar', capacidad=4, precio_noche=95000)
        ReservaServicio.check_in(self.reservar(0, 2))
        form = HabitacionForm(self.datos(tipo=familiar.pk), instance=self.hab)
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)
        # Los servicios sí se pueden actualizar.
        self.assertTrue(HabitacionForm(self.datos(servicios='Wi-Fi, TV'), instance=self.hab).is_valid())

    def test_no_cambia_a_un_tipo_con_menos_capacidad_que_una_reserva(self):
        simple = TipoHabitacion.objects.create(nombre='Simple', capacidad=1, precio_noche=45000)
        entrada = self.hoy + timedelta(days=5)
        ReservaServicio.crear(Reserva(huesped=self.huesped, habitacion=self.hab, cantidad_personas=2,
                                      fecha_entrada=entrada, fecha_salida=entrada + timedelta(days=2),
                                      estado=Reserva.Estado.CONFIRMADA))
        form = HabitacionForm(self.datos(tipo=simple.pk), instance=self.hab)
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)

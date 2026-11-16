"""
Carga datos de ejemplo para probar el sistema:

    python manage.py crear_datos_demo

Se puede ejecutar varias veces sin duplicar información.
"""
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hotel.mixins import GRUPO_CLIENTE, GRUPO_RECEPCION
from hotel.models import Habitacion, Huesped, Reserva, TipoHabitacion

TIPOS = [
    ('Simple', 'Cama de 1 plaza y media, ideal para viajes de trabajo.', 1, 45000),
    ('Doble', 'Cama de 2 plazas o dos camas de 1 plaza.', 2, 65000),
    ('Familiar', 'Cama de 2 plazas y dos camas de 1 plaza.', 4, 95000),
    ('Suite', 'Cama King, living y tina, con vista al río.', 2, 120000),
]

HABITACIONES = [
    # número, piso, tipo, servicios, estado
    ('101', 1, 'Simple', 'Wi-Fi, TV, baño privado', 'disponible'),
    ('102', 1, 'Doble', 'Wi-Fi, TV, baño privado', 'disponible'),
    ('103', 1, 'Doble', 'Wi-Fi, TV, baño privado, acceso para silla de ruedas', 'disponible'),
    ('104', 1, 'Simple', 'Wi-Fi, TV, baño privado', 'limpieza'),
    ('201', 2, 'Doble', 'Wi-Fi, TV, baño privado, vista al río', 'disponible'),
    ('202', 2, 'Familiar', 'Wi-Fi, TV, baño privado, frigobar', 'disponible'),
    ('203', 2, 'Familiar', 'Wi-Fi, TV, baño privado, frigobar', 'disponible'),
    ('204', 2, 'Doble', 'Wi-Fi, TV, baño privado', 'mantencion'),
    ('301', 3, 'Suite', 'Wi-Fi, Smart TV, tina, frigobar, vista al río', 'disponible'),
    ('302', 3, 'Suite', 'Wi-Fi, Smart TV, tina, frigobar, vista al río', 'disponible'),
]


class Command(BaseCommand):
    help = 'Crea grupos, usuarios, habitaciones, huéspedes y reservas de ejemplo.'

    def _usuario(self, username, clave, nombre, apellido, grupo=None, superusuario=False):
        usuario, creado = User.objects.get_or_create(
            username=username, defaults={'first_name': nombre, 'last_name': apellido})
        if creado:
            usuario.set_password(clave)
            usuario.is_staff = superusuario
            usuario.is_superuser = superusuario
            usuario.save()
        if grupo:
            usuario.groups.add(grupo)
        return usuario

    @transaction.atomic
    def handle(self, *args, **options):
        grupo_recepcion, _ = Group.objects.get_or_create(name=GRUPO_RECEPCION)
        grupo_cliente, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)

        self._usuario('admin', 'Admin2026!', 'Administrador', 'Hotel', superusuario=True)
        self._usuario('recepcion', 'Recepcion2026!', 'Marta', 'Rivas', grupo=grupo_recepcion)
        cliente = self._usuario('cliente', 'Cliente2026!', 'Juan', 'Pérez', grupo=grupo_cliente)

        tipos = {}
        for nombre, descripcion, capacidad, precio in TIPOS:
            tipos[nombre], _ = TipoHabitacion.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'capacidad': capacidad, 'precio_noche': precio})

        habitaciones = {}
        for numero, piso, tipo, servicios, estado in HABITACIONES:
            habitaciones[numero], _ = Habitacion.objects.get_or_create(
                numero=numero,
                defaults={'piso': piso, 'tipo': tipos[tipo], 'servicios': servicios, 'estado': estado})

        juan, _ = Huesped.objects.get_or_create(
            tipo_documento='rut', numero_documento='12345678-5',
            defaults={'nombres': 'Juan', 'apellidos': 'Pérez Soto', 'correo': 'juan.perez@example.com',
                      'telefono': '+56 9 1234 5678', 'usuario': cliente})
        maria, _ = Huesped.objects.get_or_create(
            tipo_documento='rut', numero_documento='11111111-1',
            defaults={'nombres': 'María', 'apellidos': 'González Rojas',
                      'correo': 'maria.gonzalez@example.com', 'telefono': '+56 9 8765 4321'})
        john, _ = Huesped.objects.get_or_create(
            tipo_documento='pasaporte', numero_documento='X1234567',
            defaults={'nombres': 'John', 'apellidos': 'Smith', 'correo': 'john.smith@example.com',
                      'nacionalidad': 'Estadounidense'})

        if not Reserva.objects.exists():
            hoy = timezone.localdate()
            dia = timedelta(days=1)

            def reservar(huesped, numero, entrada, salida, estado, personas=1):
                hab = habitaciones[numero]
                return Reserva.objects.create(
                    huesped=huesped, habitacion=hab, fecha_entrada=entrada, fecha_salida=salida,
                    estado=estado, cantidad_personas=personas, precio_noche=hab.tipo.precio_noche)

            # María está alojada en la 201 (check-in ayer)
            alojada = reservar(maria, '201', hoy - dia, hoy + 2 * dia, Reserva.Estado.EN_CURSO, 2)
            alojada.checkin_en = timezone.now() - dia
            alojada.save(update_fields=['checkin_en'])
            habitaciones['201'].estado = Habitacion.Estado.OCUPADA
            habitaciones['201'].save(update_fields=['estado'])

            # John llega hoy a la 102 (confirmada, lista para check-in)
            reservar(john, '102', hoy, hoy + 3 * dia, Reserva.Estado.CONFIRMADA, 2)
            # Juan pidió la Suite por la web (pendiente de confirmación)
            reservar(juan, '301', hoy + 7 * dia, hoy + 10 * dia, Reserva.Estado.PENDIENTE, 2)
            # Una estadía pasada y una cancelada para el historial
            reservar(juan, '202', hoy - 30 * dia, hoy - 27 * dia, Reserva.Estado.FINALIZADA, 3)
            reservar(maria, '302', hoy + 14 * dia, hoy + 16 * dia, Reserva.Estado.CANCELADA)

        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.'))
        self.stdout.write('Usuarios:')
        self.stdout.write('  admin      / Admin2026!      (superusuario, también accede a /admin/)')
        self.stdout.write('  recepcion  / Recepcion2026!  (recepción)')
        self.stdout.write('  cliente    / Cliente2026!    (cliente con reservas)')

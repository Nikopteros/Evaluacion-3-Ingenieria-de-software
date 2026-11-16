from django.contrib import admin

from .models import Habitacion, Huesped, Reserva, TipoHabitacion


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'precio_noche')


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'piso', 'tipo', 'estado')
    list_filter = ('estado', 'tipo', 'piso')
    search_fields = ('numero',)


@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombres', 'apellidos', 'correo', 'telefono', 'usuario')
    search_fields = ('numero_documento', 'nombres', 'apellidos', 'correo')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'huesped', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado')
    list_filter = ('estado', 'fecha_entrada')
    search_fields = ('codigo', 'huesped__nombres', 'huesped__apellidos', 'huesped__numero_documento')
    readonly_fields = ('codigo', 'precio_noche', 'creada_por', 'checkin_en', 'checkout_en', 'cancelada_en')

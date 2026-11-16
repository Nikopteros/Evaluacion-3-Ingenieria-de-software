from django.urls import path

from . import views

app_name = 'hotel'

urlpatterns = [
    # Público (invitado)
    path('', views.inicio, name='inicio'),
    path('habitaciones/', views.catalogo, name='catalogo'),
    path('disponibilidad/', views.consultar_disponibilidad, name='disponibilidad'),
    path('registro/', views.registro, name='registro'),
    path('redireccion/', views.redireccion, name='redireccion'),

    # Cliente
    path('mis-reservas/', views.MisReservasView.as_view(), name='mis_reservas'),
    path('reservar/<int:habitacion_id>/', views.ReservaClienteCreateView.as_view(), name='reservar'),
    path('mis-reservas/<int:pk>/cancelar/', views.ClienteCancelarReservaView.as_view(),
         name='cliente_cancelar'),

    # Recepción: panel de ocupación
    path('recepcion/', views.PanelView.as_view(), name='panel'),

    # Recepción: habitaciones y tipos
    path('recepcion/habitaciones/', views.HabitacionListView.as_view(), name='habitacion_lista'),
    path('recepcion/habitaciones/nueva/', views.HabitacionCreateView.as_view(), name='habitacion_nueva'),
    path('recepcion/habitaciones/<int:pk>/editar/', views.HabitacionUpdateView.as_view(),
         name='habitacion_editar'),
    path('recepcion/habitaciones/<int:pk>/estado/', views.HabitacionEstadoView.as_view(),
         name='habitacion_estado'),
    path('recepcion/tipos/', views.TipoListView.as_view(), name='tipo_lista'),
    path('recepcion/tipos/nuevo/', views.TipoCreateView.as_view(), name='tipo_nuevo'),
    path('recepcion/tipos/<int:pk>/editar/', views.TipoUpdateView.as_view(), name='tipo_editar'),

    # Recepción: huéspedes
    path('recepcion/huespedes/', views.HuespedListView.as_view(), name='huesped_lista'),
    path('recepcion/huespedes/nuevo/', views.HuespedCreateView.as_view(), name='huesped_nuevo'),
    path('recepcion/huespedes/<int:pk>/', views.HuespedDetailView.as_view(), name='huesped_detalle'),
    path('recepcion/huespedes/<int:pk>/editar/', views.HuespedUpdateView.as_view(), name='huesped_editar'),

    # Recepción: reservas, check-in y check-out
    path('recepcion/reservas/', views.ReservaListView.as_view(), name='reserva_lista'),
    path('recepcion/reservas/nueva/', views.ReservaCreateView.as_view(), name='reserva_nueva'),
    path('recepcion/reservas/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva_detalle'),
    path('recepcion/reservas/<int:pk>/confirmar/', views.AccionReservaView.as_view(accion='confirmar'),
         name='reserva_confirmar'),
    path('recepcion/reservas/<int:pk>/cancelar/', views.AccionReservaView.as_view(accion='cancelar'),
         name='reserva_cancelar'),
    path('recepcion/reservas/<int:pk>/check-in/', views.AccionReservaView.as_view(accion='checkin'),
         name='reserva_checkin'),
    path('recepcion/reservas/<int:pk>/check-out/', views.AccionReservaView.as_view(accion='checkout'),
         name='reserva_checkout'),
]

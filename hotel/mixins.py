"""
Roles del sistema (ver diagrama de casos de uso):

  - Invitado    → usuario sin sesión: ve habitaciones y consulta disponibilidad.
  - Cliente     → usuario registrado con perfil de huésped: reserva, ve y cancela sus reservas.
  - Recepción   → grupo "Recepcion" (o superusuario): gestiona habitaciones, huéspedes y reservas.
"""
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

GRUPO_RECEPCION = 'Recepcion'
GRUPO_CLIENTE = 'Cliente'


def es_recepcion(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=GRUPO_RECEPCION).exists()


def es_cliente(user):
    return user.is_authenticated and hasattr(user, 'huesped')


class RecepcionRequeridaMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return es_recepcion(self.request.user)


class ClienteRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return es_cliente(self.request.user)


recepcion_requerida = user_passes_test(es_recepcion)

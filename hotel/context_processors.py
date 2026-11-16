from .mixins import es_cliente, es_recepcion


def roles(request):
    """Deja disponibles `es_recepcion` y `es_cliente` en todas las plantillas."""
    user = request.user
    return {'es_recepcion': es_recepcion(user), 'es_cliente': es_cliente(user)}

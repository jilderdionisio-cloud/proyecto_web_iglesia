from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError


def date_param(request, name):
    """Lee una fecha opcional de la URL; un valor inválido responde 400 en lugar de 500."""
    raw = request.query_params.get(name)
    if not raw:
        return None
    try:
        value = parse_date(raw)
    except ValueError:
        value = None
    if value is None:
        raise ValidationError({name: 'Usa una fecha válida con formato AAAA-MM-DD.'})
    return value


def int_param(request, name):
    raw = request.query_params.get(name)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValidationError({name: 'Debe ser un número entero.'})


def date_range(request):
    start, end = date_param(request, 'from'), date_param(request, 'to')
    if start and end and start > end:
        raise ValidationError({'from': 'La fecha inicial no puede ser posterior a la final.'})
    return start, end

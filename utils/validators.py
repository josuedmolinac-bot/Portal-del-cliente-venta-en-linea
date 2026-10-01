def is_positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


MAX_SEARCH_LENGTH = 100
AVAILABILITY_OPTIONS = ("Disponible", "Stock limitado", "Sin stock")


class FilterValidationError(ValueError):
    pass


def normalize_search_text(value):
    normalized = " ".join((value or "").split())
    if len(normalized) > MAX_SEARCH_LENGTH:
        raise FilterValidationError(
            f"La búsqueda no puede superar {MAX_SEARCH_LENGTH} caracteres."
        )
    return normalized


def validate_choice(value, allowed_values, field_label):
    normalized = (value or "").strip()
    if normalized and normalized not in allowed_values:
        raise FilterValidationError(f"{field_label} no es válido.")
    return normalized


def parse_non_negative_price(value, field_label):
    normalized = (value or "").strip()
    if not normalized:
        return None
    if not normalized.isdecimal():
        raise FilterValidationError(f"{field_label} debe ser un número entero.")
    price = int(normalized)
    if price < 0:
        raise FilterValidationError(f"{field_label} no puede ser negativo.")
    return price


def validate_price_range(minimum, maximum):
    if minimum is not None and maximum is not None and minimum > maximum:
        raise FilterValidationError(
            "El precio mínimo no puede ser mayor que el precio máximo."
        )


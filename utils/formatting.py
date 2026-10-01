def format_clp(value):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("El precio debe ser un entero no negativo.")
    return f"${value:,}".replace(",", ".")


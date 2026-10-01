def is_positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


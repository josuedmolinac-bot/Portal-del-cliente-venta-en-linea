import pytest

from services.catalog_service import get_availability


@pytest.mark.parametrize(("stock", "expected"), [(0, "Sin stock"), (-1, "Sin stock"), (1, "Stock limitado"), (5, "Stock limitado"), (6, "Disponible")])
def test_availability_is_derived_from_stock(stock, expected):
    assert get_availability(stock) == expected


@pytest.mark.parametrize("stock", [None, "5", 2.5, True])
def test_availability_rejects_invalid_stock(stock):
    with pytest.raises(ValueError):
        get_availability(stock)


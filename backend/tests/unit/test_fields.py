from datetime import date

import pytest

from app.shared.validation import fields as fv


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("15.06.1992", date(1992, 6, 15)),
        ("15/06/1992", date(1992, 6, 15)),
        ("1-2-2000", date(2000, 2, 1)),
        ("I5.O6.1992", date(1992, 6, 15)),
        ("31.02.1990", None),
        ("abc", None),
        (None, None),
    ],
)
def test_parse_date(raw, expected):
    assert fv.parse_date(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("1.75", 1.75), ("1,80", 1.8), ("3.50", None), ("abc", None), ("0.20", None)])
def test_parse_height(raw, expected):
    assert fv.parse_height_m(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("M", "M"), (" f ", "F"), ("X", None), ("", None)])
def test_parse_sex(raw, expected):
    assert fv.parse_sex(raw) == expected


def test_clean_name_keeps_accents_and_rejects_noise():
    assert fv.clean_name("  Atángana   Mohammadou ") == "Atángana Mohammadou"
    assert fv.clean_name("12345") is None
    assert fv.clean_name("A") is None
    assert fv.clean_name("N'Guéma-Ondoa") == "N'Guéma-Ondoa"


def test_canonical_removes_accents_and_case():
    assert fv.canonical("  Atángana  mohammadou") == "ATANGANA MOHAMMADOU"


def test_full_years_boundaries():
    born = date(2000, 6, 15)
    assert fv.full_years(born, date(2018, 6, 14)) == 17
    assert fv.full_years(born, date(2018, 6, 15)) == 18

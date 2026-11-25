from app.shared.ocr.cni_cameroun import extract_cni_cameroun
from tests.helpers import cni_lines


def test_extracts_all_fields_from_card_sample():
    result = extract_cni_cameroun(cni_lines())
    texts = {name: field.text for name, field in result.fields.items()}
    assert texts == {
        "surname": "Atángana Mohammadou",
        "given_names": "SALAH",
        "date_of_birth": "15.06.1992",
        "place_of_birth": "Baffousam",
        "sex": "M",
        "height": "1.75",
        "profession": "Footballer",
    }
    assert result.header_found is True


def test_garbled_place_label_falls_back_to_position():
    place = extract_cni_cameroun(cni_lines()).fields["place_of_birth"]
    assert place.method == "inferred"
    assert place.text == "Baffousam"


def test_readable_place_label_is_matched_directly():
    place = extract_cni_cameroun(cni_lines(place_label_readable=True)).fields["place_of_birth"]
    assert (place.method, place.text) == ("label", "Baffousam")


def test_missing_header_is_reported():
    assert extract_cni_cameroun(cni_lines(header=False)).header_found is False


def test_empty_input_yields_nothing():
    result = extract_cni_cameroun([])
    assert result.fields == {} and result.line_count == 0


def test_labels_are_never_returned_as_values():
    values = {f.text for f in extract_cni_cameroun(cni_lines()).fields.values()}
    assert not any("SURNAME" in v or "BIRTH" in v for v in values)

import typing

import pytest


from ._summary import iso_duration_pt, _parse_to_days


@pytest.mark.parametrize(
    "value, years, months, days, hours, minutes, seconds",
    [
        ("P3Y6M4DT12H30M5S", "3", "6", "4", "12", "30", "5"),
        ("P3Y6M4D", "3", "6", "4", None, None, None),
        ("P3Y", "3", None, None, None, None, None),
        ("P6M", None, "6", None, None, None, None),
        ("P4D", None, None, "4", None, None, None),
    ],
)
def test_iso_duration_pt__ok_values(
    value: str,
    years: typing.Optional[str],
    months: typing.Optional[str],
    days: typing.Optional[str],
    hours: typing.Optional[str],
    minutes: typing.Optional[str],
    seconds: typing.Optional[str],
):
    match = iso_duration_pt.match(value)

    assert match is not None

    assert match.group("years") == years
    assert match.group("months") == months
    assert match.group("days") == days
    assert match.group("hours") == hours
    assert match.group("minutes") == minutes
    assert match.group("seconds") == seconds


@pytest.mark.parametrize(
    "value, expected",
    [
        ("P3Y6M4DT12H30M5S", 1280.27089,),
        ("P3Y6M4D", 1279.75,),
        ("P3Y", 1095.75,),
        ("P3Y4M", 1215.75,),
        ("P6M", 180.,),
        ("P4D", 4.,),
        ("PT12H", .5,),
        ("PT1S", .00001157407,),
    ],
)
def test__parse_to_days(
    value: str,
    expected: float,
):
    actual = _parse_to_days(value)

    assert actual == pytest.approx(expected)

import pytest

import data.geolocation as geo


def test_abc_base():
    with pytest.raises(TypeError):
        geo.GeoLocation(geo.TEST_LAT, geo.TEST_LON)


# --- DecimalDegrees ---

def test_construct_decimal():
    loc = geo.DecimalDegrees(geo.TEST_LAT, geo.TEST_LON)
    assert isinstance(loc, geo.DecimalDegrees)


def test_decimal_bad_lat_type():
    with pytest.raises(TypeError):
        geo.DecimalDegrees('40.7', geo.TEST_LON)


def test_decimal_bad_lon_type():
    with pytest.raises(TypeError):
        geo.DecimalDegrees(geo.TEST_LAT, '-74.0')


def test_decimal_lat_too_high():
    with pytest.raises(ValueError):
        geo.DecimalDegrees(91.0, geo.TEST_LON)


def test_decimal_lat_too_low():
    with pytest.raises(ValueError):
        geo.DecimalDegrees(-91.0, geo.TEST_LON)


def test_decimal_lon_too_high():
    with pytest.raises(ValueError):
        geo.DecimalDegrees(geo.TEST_LAT, 181.0)


def test_decimal_lon_too_low():
    with pytest.raises(ValueError):
        geo.DecimalDegrees(geo.TEST_LAT, -181.0)


def test_decimal_boundary_lat_max():
    loc = geo.DecimalDegrees(90.0, geo.TEST_LON)
    assert loc.lat == 90.0


def test_decimal_boundary_lat_min():
    loc = geo.DecimalDegrees(-90.0, geo.TEST_LON)
    assert loc.lat == -90.0


def test_decimal_boundary_lon_max():
    loc = geo.DecimalDegrees(geo.TEST_LAT, 180.0)
    assert loc.lon == 180.0


def test_decimal_accepts_int():
    loc = geo.DecimalDegrees(40, -74)
    assert isinstance(loc, geo.DecimalDegrees)


def test_decimal_str():
    loc = geo.DecimalDegrees(geo.TEST_LAT, geo.TEST_LON)
    assert str(loc) == f'{geo.TEST_LAT}, {geo.TEST_LON}'


# --- DMSLocation ---

def test_construct_dms():
    loc = geo.DMSLocation(geo.TEST_DMS_LAT, geo.TEST_DMS_LON)
    assert isinstance(loc, geo.DMSLocation)


def test_dms_bad_lat_type():
    with pytest.raises(TypeError):
        geo.DMSLocation(40, geo.TEST_DMS_LON)


def test_dms_bad_lon_type():
    with pytest.raises(TypeError):
        geo.DMSLocation(geo.TEST_DMS_LAT, 74)


def test_dms_bad_lat_format():
    with pytest.raises(ValueError):
        geo.DMSLocation('40N', geo.TEST_DMS_LON)


def test_dms_bad_lon_format():
    with pytest.raises(ValueError):
        geo.DMSLocation(geo.TEST_DMS_LAT, '74W')


def test_dms_wrong_hemisphere_lat():
    """Longitude hemisphere letter in a latitude position should fail."""
    with pytest.raises(ValueError):
        geo.DMSLocation("40°42'46\"E", geo.TEST_DMS_LON)


def test_dms_wrong_hemisphere_lon():
    """Latitude hemisphere letter in a longitude position should fail."""
    with pytest.raises(ValueError):
        geo.DMSLocation(geo.TEST_DMS_LAT, "74°0'22\"N")


def test_dms_lat_degrees_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation("91°0'0\"N", geo.TEST_DMS_LON)


def test_dms_lon_degrees_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation(geo.TEST_DMS_LAT, "181°0'0\"E")


def test_dms_lat_minutes_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation("40°60'0\"N", geo.TEST_DMS_LON)


def test_dms_lon_minutes_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation(geo.TEST_DMS_LAT, "74°60'0\"W")


def test_dms_lat_seconds_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation("40°42'60\"N", geo.TEST_DMS_LON)


def test_dms_lon_seconds_out_of_range():
    with pytest.raises(ValueError):
        geo.DMSLocation(geo.TEST_DMS_LAT, "74°0'60\"W")


def test_dms_str():
    loc = geo.DMSLocation(geo.TEST_DMS_LAT, geo.TEST_DMS_LON)
    assert str(loc) == f'{geo.TEST_DMS_LAT}, {geo.TEST_DMS_LON}'

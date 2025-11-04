# TODO (api): Countries REST API namespace
# - Namespace path: /api/v1/countries
# - Define flask-restx model 'Country' for request/response (code, name, population, area_km2, meta)
# - Routes to implement:
#   POST   /api/v1/countries
#   GET    /api/v1/countries
#   GET    /api/v1/countries/<code>
#   PUT    /api/v1/countries/<code>
#   PATCH  /api/v1/countries/<code>  (optional)
#   DELETE /api/v1/countries/<code>
# - Each route should call the corresponding data.countries.* wrapper and return proper HTTP codes:
#   201 (create), 200 (ok), 204 (delete), 404 (not found), 400 (validation), 409 (duplicate)
# - Tests for this module should use mongomock and Flask test client (tests/test_api_countries.py)
API_PREFIX = "/api/v1"
KNOWN_MODULES = frozenset({"kyc", "kyb", "biometrics"})
ALLOWED_IMAGE_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png"}
IMAGE_SIGNATURES = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")
MAX_IMAGE_PIXELS = 40_000_000
MAX_IMAGE_SIDE_PX = 2400
SHARPNESS_MIN = 25.0
REQUEST_ID_HEADER = "X-Request-ID"

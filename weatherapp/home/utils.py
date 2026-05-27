from string import capwords

from django.utils.text import slugify

try:
    from babel import Locale
except ImportError:  # pragma: no cover - optional dependency
    Locale = None


COUNTRY_SUGGESTIONS = [
    "India",
    "United States",
    "United Kingdom",
    "Australia",
    "Canada",
    "Singapore",
    "United Arab Emirates",
]

COUNTRY_CODE_FALLBACKS = {
    "AE": "United Arab Emirates",
    "AU": "Australia",
    "CA": "Canada",
    "GB": "United Kingdom",
    "IN": "India",
    "SG": "Singapore",
    "US": "United States",
}

INDIAN_STATE_SUGGESTIONS = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]


def normalize_whitespace(value):
    return " ".join((value or "").split())


def normalize_place_name(value):
    return capwords(normalize_whitespace(value))


def join_place_parts(*parts):
    cleaned_parts = []
    seen = set()

    for part in parts:
        normalized = normalize_place_name(part)
        if not normalized:
            continue

        key = normalized.lower()
        if key in seen:
            continue

        seen.add(key)
        cleaned_parts.append(normalized)

    return ", ".join(cleaned_parts)


def country_name_from_code(value):
    code = normalize_whitespace(value).upper()
    if not code:
        return ""

    if Locale is not None:
        try:
            return normalize_place_name(Locale.parse("en").territories.get(code, code))
        except Exception as e:  # pragma: no cover - defensive fallback
            import logging; logging.warning(f'Locale parsing failed: {e}')

    return COUNTRY_CODE_FALLBACKS.get(code, code)


def normalize_state_key(value):
    return normalize_whitespace((value or "").replace("-", " ")).lower()


def display_state_name(value):
    return capwords(normalize_state_key(value))


def state_slug(value):
    return slugify(normalize_state_key(value))

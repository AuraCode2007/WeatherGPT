"""
backend/utils/location_parser.py
Extract a city/location name from a free-text user query.
Supports English and transliterated Indian city names.
"""
import re

# Trigger patterns — handles "in Delhi", "for Mumbai", "at Pune" etc.
_PATTERNS = [
    r"\bin\s+([A-Za-z\s\-\.]+?)(?:\?|$|,|\s+today|\s+tomorrow|\s+this|\s+next|\s+on)",
    r"\bfor\s+([A-Za-z\s\-\.]+?)(?:\?|$|,|\s+today|\s+tomorrow|\s+this|\s+next|\s+on)",
    r"\bat\s+([A-Za-z\s\-\.]+?)(?:\?|$|,|\s+today|\s+tomorrow|\s+this|\s+next|\s+on)",
    r"\bnear\s+([A-Za-z\s\-\.]+?)(?:\?|$|,|\s+today|\s+tomorrow|\s+this|\s+next|\s+on)",
    r"\bweather\s+(?:of\s+)?([A-Za-z\s\-\.]+?)(?:\?|$|,|\s+today|\s+tomorrow|\s+this|\s+next|\s+on)",
]

DEFAULT_CITY = "Delhi"

# Known major Indian cities for quick lookup
KNOWN_CITIES: set[str] = {
    "delhi","mumbai","bangalore","bengaluru","chennai","kolkata","hyderabad",
    "pune","ahmedabad","jaipur","surat","lucknow","kanpur","nagpur","indore",
    "bhopal","visakhapatnam","vizag","patna","vadodara","ghaziabad","ludhiana",
    "agra","nashik","faridabad","meerut","rajkot","kalyan","varanasi","srinagar",
    "aurangabad","dhanbad","amritsar","allahabad","prayagraj","ranchi","coimbatore",
    "jabalpur","gwalior","vijayawada","jodhpur","madurai","raipur","kota","chandigarh",
    "guwahati","solapur","hubli","tiruchirappalli","trichy","bareilly","moradabad",
    "mysore","bhubaneswar","thiruvananthapuram","trivandrum","kochi","mangalore",
    "shimla","dehradun","haridwar","rishikesh","nainital","mussoorie","ooty",
}


def extract_city(query: str) -> str:
    """
    Try to pull a city name from the query string.
    Returns the matched city (Title-cased), or DEFAULT_CITY.
    """
    q = query.strip()

    # Direct known-city match first (fast path)
    q_words = q.lower().split()
    for word in q_words:
        clean = re.sub(r"[^a-z]", "", word)
        if clean in KNOWN_CITIES:
            return clean.title()

    # Regex extraction
    for pattern in _PATTERNS:
        match = re.search(pattern, q, re.IGNORECASE)
        if match:
            city = match.group(1).strip().title()
            if 2 <= len(city) <= 40:
                return city

    return DEFAULT_CITY

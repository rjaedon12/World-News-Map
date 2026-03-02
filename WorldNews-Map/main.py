import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pycountry
import reverse_geocoder as rg

# ── MUST be first Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="World News Map",
    page_icon="🌍",
    layout="wide",
)


def coords_to_country(lat: float, lon: float):
    """
    Return (alpha2_lower, country_name) for the clicked coordinates.
    Uses reverse_geocoder (offline, no API cost) to find the nearest
    populated place and its ISO-3166-1 alpha-2 country code.
    """
    try:
        results = rg.search((lat, lon), verbose=False)
        if results:
            raw_cc = results[0]["cc"]                          # e.g. "US"
            cc = raw_cc.lower()                                # gnews wants lowercase
            country_obj = pycountry.countries.get(alpha_2=raw_cc.upper())
            name = country_obj.name if country_obj else raw_cc
            return cc, name
    except Exception as e:
        st.warning(f"Reverse geocode failed: {e}")
    return None, None


# ── GNews API helper ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_news(country_code: str):
    """
    Fetch top headlines from GNews for a given ISO-3166-1 alpha-2 country code.
    Cached – API called ONCE per unique country until server restarts.
    Token cost: 1 token per article returned.  max=3 → 3 tokens per new country.
    Repeated clicks on the same country cost 0 (served from cache).
    """
    if not country_code:
        return []
    try:
        response = requests.get(
            "https://gnews.io/api/v4/top-headlines",
            params={
                "country":  country_code,
                "token":    "375aa2b2d418e57fa443ba82b5a829db",
                "category": "general",
                "language": "en",        # MUST be "en", not "English"
                "max":      1,           # integer, not string → 3 tokens
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.HTTPError as e:
        st.error(f"GNews API error {e.response.status_code}: {e.response.text}")
        return []
    except Exception as e:
        st.error(f"Request failed: {e}")
        return []


# ── Session state ─────────────────────────────────────────────────────────────
if "country_code" not in st.session_state:
    st.session_state.country_code = "us"
if "country_name" not in st.session_state:
    st.session_state.country_name = "United States"
if "click_lat" not in st.session_state:
    st.session_state.click_lat = None
if "click_lon" not in st.session_state:
    st.session_state.click_lon = None

# ── UI ────────────────────────────────────────────────────────────────────────
st.title(" World News Map")
st.caption("Click any country on the map to load its top headlines.")

# ── Build map ─────────────────────────────────────────────────────────────────
world_map = folium.Map(location=[20.0, 0.0], zoom_start=2, tiles="CartoDB positron")

if st.session_state.click_lat is not None:
    folium.Marker(
        location=[st.session_state.click_lat, st.session_state.click_lon],
        tooltip=st.session_state.country_name,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(world_map)

output = st_folium(world_map, width=1400, height=500, returned_objects=["last_clicked"])

# ── Handle click ──────────────────────────────────────────────────────────────
clicked_coords = output.get("last_clicked")

if clicked_coords:
    lat = clicked_coords["lat"]
    lon = clicked_coords["lng"]
    cc, name = coords_to_country(lat, lon)
    if cc:
        st.session_state.country_code = cc
        st.session_state.country_name = name
        st.session_state.click_lat    = lat
        st.session_state.click_lon    = lon
    else:
        st.warning("Could not determine country from that location.")

country_code = st.session_state.country_code
country_name = st.session_state.country_name

# ── Headline & news ───────────────────────────────────────────────────────────
st.subheader(f" Top headlines for: **{country_name}** (`{country_code.upper()}`)")

with st.spinner(f"Fetching news for {country_name}…"):
    articles = get_news(country_code)

if not articles:
    st.info("No articles found. This country may not be supported by GNews, or your API key is invalid.")
else:
    for article in articles:
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                if article.get("image"):
                    st.image(article["image"], use_container_width=True)
            with cols[1]:
                st.markdown(f"### [{article.get('title', 'No title')}]({article.get('url', '#')})")
                st.caption(
                    f" {article.get('source', {}).get('name', 'Unknown')}  •  "
                    f" {article.get('publishedAt', '')[:10]}"
                )
                st.write(article.get("description", ""))
            st.divider()

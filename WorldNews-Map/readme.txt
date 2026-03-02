Dependencies you must install
- streamlit
- python (3.14x)
- folium
- pycountry
- reverse_geocoder

API key setup
- Get a free GNews API key from https://gnews.io/
- When the app runs, enter your key in the sidebar text input.
- Optionally, create a .streamlit/secrets.toml file with:
    GNEWS_API_KEY = "your_key_here"
  and the app will use it automatically without needing the sidebar input.

Once all dependencies are installed run...
streamlit run /Users/your_username/WorldNews-Map/main.py

N.B Some countries do not work because the news api does not have access to those sources
Enjoy!
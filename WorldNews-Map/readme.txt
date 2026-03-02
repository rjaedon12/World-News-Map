Dependencies you must install
- streamlit
- python (3.14x)
- folium
- pycountry
- reverse_geocoder

API key setup
- Get a free GNews API key from https://gnews.io/

Local Streamlit app (main.py):
- Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml
- Fill in your real key: GNEWS_API_KEY = "your_key_here"
- The app reads the key automatically; the sidebar input is shown as a fallback.
- secrets.toml is listed in .gitignore and will never be committed.

GitHub Pages (index.html) – deployed via GitHub Actions:
- Go to your repository Settings → Secrets and variables → Actions
- Add a new secret named GNEWS_API_KEY with your key as the value.
- The build workflow will inject it automatically on every push to main.

Once all dependencies are installed run...
streamlit run /Users/your_username/WorldNews-Map/main.py

N.B Some countries do not work because the news api does not have access to those sources
Enjoy!
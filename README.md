## Demo

▶️ Watch demo (inline player)

https://github.com/user-attachments/assets/84ea1205-f4de-4495-b98c-e05d89f3a4ed

## Spotify setup

1. **Create a Spotify app** at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) → Create app.
2. **Configure Redirect URI** (Settings → Redirect URIs):
   - Add exactly: `http://127.0.0.1:8501`
   - Do **not** use `http://localhost:8501` — Spotify does not allow `localhost` for redirect URIs ([redirect URI docs](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)).
   - Save changes in the dashboard.
3. **Copy credentials** from the app Settings page into `.env`:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8501
```

(`SPOTIFY_REDIRECT_URI` is optional if left at the default above.)

4. **Run the app** (`streamlit run app.py`), open the UI, and click **Connect Spotify**. After login, Spotify redirects to `http://127.0.0.1:8501?code=...` (same Streamlit server even if you browsed via `localhost:8501`).

### Troubleshooting

- **`redirect_uri: Not matching configuration`** — The redirect URI in the authorize URL must match the dashboard **exactly**. Use `http://127.0.0.1:8501`, not `localhost`. Confirm the URI is saved in Dashboard → Settings → Redirect URIs, then restart Streamlit after editing `.env`.
- The UI shows the active redirect URI under the Connect Spotify button for verification.
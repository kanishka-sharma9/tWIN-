# Setting up Google sign-in

tWIN!! can let people sign up and log in with a Google account. It is off until you create an OAuth client at Google and give its details to the API. While it is off, the button is hidden and email and password works on its own.

The API runs the whole flow (authorization code with PKCE). The browser only follows redirects, and no Google secret ever reaches it.

## 1. Create a Google Cloud project

1. Open the [Google Cloud console](https://console.cloud.google.com/) and sign in.
2. Use the project picker at the top, choose **New project**, name it (for example `twin`) and create it. Select it afterwards.

## 2. Configure the OAuth consent screen

1. Go to **APIs & Services > OAuth consent screen** (Google may call this **Google Auth Platform > Branding**).
2. Choose the **External** user type and create.
3. Fill in the app name (`tWIN!!`), a support email and a developer contact email.
4. Scopes: tWIN!! asks for `openid` and `email` only. These are not sensitive, so no Google review is needed.
5. While the publishing status is **Testing**, only the Google accounts you add under **Test users** can sign in. Move to **In production** when you are ready for everyone.

## 3. Create the OAuth client

1. Go to **APIs & Services > Credentials > Create credentials > OAuth client ID**.
2. Application type: **Web application**. Name it anything.
3. Under **Authorized redirect URIs** add the callback exactly as the API will be reached:
   - local development: `http://localhost:8000/api/auth/google/callback`
   - a deployed site: `https://<your-domain>/api/auth/google/callback`

   The value must match `TWIN_GOOGLE_REDIRECT_URI` character for character. Google accepts plain `http` only for `localhost`.
4. Create, then copy the **Client ID** and **Client secret**. Treat the secret like a password.

## 4. Set the environment variables

Put these in the root `.env` (never commit it) or in the environment of the API process:

```bash
TWIN_GOOGLE_CLIENT_ID=<client id>.apps.googleusercontent.com
TWIN_GOOGLE_CLIENT_SECRET=<client secret>
TWIN_GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

`TWIN_GOOGLE_REDIRECT_URI` defaults to the local value above. Google sign-in is on only when the client id, the secret and the redirect URI are all set and not empty. Restart the API after changing them.

When the site is served over HTTPS also set `TWIN_COOKIE_SECURE=true`.

## 5. Check it

- `GET /api/auth/providers` answers `{"google": true}`.
- Open `/api/auth/google/start` in a browser. You should land on Google's account chooser, and after you approve you are sent to `/` logged in.
- Signing in with an address that already has a password account sends you to `/login?error=account_exists`. Accounts are never linked automatically (D-030).

If Google shows `redirect_uri_mismatch`, the URI in the console and `TWIN_GOOGLE_REDIRECT_URI` differ (scheme, host, port, path or a trailing slash).

## How the API uses it

- `GET /api/auth/google/start` redirects to Google with a random `state` and a PKCE S256 challenge. The `state` and the PKCE verifier travel in a signed, httpOnly, ten-minute cookie scoped to `/api/auth/google`.
- `GET /api/auth/google/callback` checks the `state` against that cookie, exchanges the code with Google, and checks the ID token's issuer, audience, expiry and `email_verified`. A known Google subject logs in; a new subject with an unused email creates the account and vault; an email that already has an account is refused.

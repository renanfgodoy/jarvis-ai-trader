# Repository hygiene

## Policy

- Generated dependencies are not versioned.
- Rebuild frontend dependencies with `npm install` or `npm ci` inside `frontend/`.
- Build outputs and local caches do not belong in Git.
- Never version `.env`, HAR files, credentials, tokens, cookies, bearer values, authorization headers, refresh tokens, SSID values or `.jarvis_cache/` content.

## Ignored generated paths

- `frontend/node_modules/`
- `frontend/dist/`
- `frontend/.vite/`
- `node_modules/`
- `dist/`
- `.pytest_cache/`
- `__pycache__/`
- `*.py[cod]`
- `.jarvis_cache/`
- `.jarvis_cache_test/`

## Notes from Sprint 1 repository hygiene

The numbered `.gitignore` copies were older duplicates and did not contain
rules missing from the official `.gitignore`.

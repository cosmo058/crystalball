# Crystalball — Frontend

React + Vite single-page app. Communicates with the FastAPI backend at `/api/*` (proxied through Vite in dev, through nginx in production).

## Dev setup

```bash
npm install
npm run dev        # http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:8000` — make sure the backend is running first.

## Build

```bash
npm run build      # output in dist/
```

In Docker the build output is served by nginx which also reverse-proxies `/api` to the backend container.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `` (empty) | Override API base URL if needed |

See the root [`README.md`](../README.md) for full project documentation.

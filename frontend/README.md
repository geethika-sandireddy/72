# INDRA frontend (Next.js)

This replaced the earlier static HTML/CSS/JS dashboard. It is a real
Next.js 16 + React 19 + Tailwind app — it does **not** run by opening a
file in a browser. You need a dev server.

## Run it

```bash
cd frontend
npm install      # or pnpm install, if you have pnpm
npm run dev
```

Then open http://localhost:3000

## Build for production

```bash
npm run build
npm run start
```

## Connecting to the backend

The dashboard's hero content, storm cells and KPIs (`lib/indra-data.ts`)
are still fixed, labelled SYNTHETIC demo data — that's intentional, so
the console always looks right even with no backend running.

On top of that, the app now also talks to the real FastAPI backend
(`app/service.py`):

1. Start the backend: `uvicorn app.service:app --reload` (from the repo root).
2. Start the frontend: `cd frontend && npm run dev`.
3. The top bar shows a **BACKEND LIVE** / **BACKEND OFFLINE** pill (polls
   `GET /health` every 15s).
4. In the operations console, click **Ping live backend** to send a real
   `POST /forecast` for the selected cell and see the actual latency and
   model output returned by the backend.

If your backend runs somewhere other than `http://localhost:8000`, copy
`.env.example` to `.env.local` and set `NEXT_PUBLIC_API_BASE_URL`.

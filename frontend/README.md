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

## Status

`lib/indra-data.ts` currently ships fixed SYNTHETIC demo data (storm
cells, source health, benchmark numbers) — it does not yet call the
FastAPI backend in `app/service.py`. Wiring it to `POST /forecast` is
the same kind of integration that was done for the old static
dashboard and is the next step before this can show live data.

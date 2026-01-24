# WLED Manager UI

A modern Vue.js SPA for managing WLED devices on your network.

## Features

- Dark mode support
- Admin dashboard layout
- Responsive design with TailwindCSS
- Integration with WLED Manager API

## Tech Stack

- Vue 3 with TypeScript
- Vite for build tool
- TailwindCSS for styling
- FastAPI backend integration

## Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

The application uses Vite environment variables for configuration. Create a `.env` file in the root directory to override the default settings:

```
VITE_API_PROTOCOL=http
VITE_API_HOST=localhost
VITE_API_PORT=8000
```

For production builds, create a `.env.production` file with your production settings:

```
VITE_API_PROTOCOL=https
VITE_API_HOST=wled-manager-api.example.com
VITE_API_PORT=443
```

3. Open [http://localhost:5174](http://localhost:5174) in your browser.

## Build

```bash
npm run build
```

## API Integration

This UI is designed to work with the WLED Manager API server running on `http://127.0.0.1:8000`.

Make sure to start the API server first:
```bash
uvicorn api.server:app --reload
```

To disable the periodic health check process (runs every 30 seconds):
```bash
DISABLE_HEALTH_CHECK=true uvicorn api.server:app --reload
```

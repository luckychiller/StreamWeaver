# StreamWeaver Frontend

The frontend component of StreamWeaver, a real-time data ingestion pipeline dashboard built with React, TypeScript, and Vite.

## Overview

This React application provides a real-time dashboard that visualizes data streams from the StreamWeaver backend, including:
- Stock trades
- Social media posts
- Server logs

The dashboard connects to the backend WebSocket server to receive live updates and displays them in an intuitive interface.

## Features

- Real-time data visualization
- Modular component architecture
- WebSocket integration for live updates
- Responsive design
- Type-safe development with TypeScript

## Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173` (default Vite port).

Note: For the full experience with live data, ensure the backend services are running. The frontend is typically run as part of the complete Docker Compose setup in the root directory.

## Project Structure

```
frontend/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI elements
│   └── ...             # Feature-specific components
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── public/             # Static assets
└── types.ts            # TypeScript type definitions
```

## Building for Production

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Development

- Uses Vite for fast development and building
- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for styling (if configured)

## Connecting to Backend

The frontend automatically connects to the WebSocket server at `ws://localhost:8080` when running. Ensure the backend WebSocket service is active for real-time data.

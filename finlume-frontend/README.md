# Finlume Frontend

A modern, responsive Vite + React + TypeScript + Tailwind CSS web dashboard for the Finlume AI companion app.

## Features

- **Vite & React (TypeScript)**: Extremely fast development server and optimized production builds.
- **Tailwind CSS**: Utility-first CSS framework for modern designs.
- **Routing**: Set up using `react-router-dom` with `/login` and `/dashboard` paths.
- **Framer Motion**: Configured for animations and micro-interactions.
- **Recharts**: Ready to render charts for data visualization.
- **Axios HTTP Client**: Set up with a JWT localStorage request interceptor at [src/lib/api.ts](src/lib/api.ts).
- **Sidebar Shell Component**: Styled navigation sidebar with placeholders for all major financial views.

## Project Structure

```text
finlume-frontend/
├── src/
│   ├── assets/        # Media assets
│   ├── components/    # Reusable UI components (e.g. Sidebar)
│   ├── hooks/         # Custom React hooks (with placeholder)
│   ├── lib/           # Custom helper libraries (e.g. Axios api client)
│   ├── pages/         # Page components (e.g. LoginPage, DashboardPage)
│   ├── routes/        # Router configuration and paths (with placeholder)
│   ├── types/         # TypeScript type definitions (with placeholder)
│   ├── App.tsx        # Application routing layout
│   ├── index.css      # Tailwind CSS imports
│   └── main.tsx       # Entrypoint file
├── .env               # Local configuration environment file
├── .env.example       # Environment template
├── .gitignore         # Build & node exclusions
├── postcss.config.js  # PostCSS config for Tailwind
├── tailwind.config.js # Tailwind CSS configuration
└── tsconfig.json      # TypeScript compiler choices
```

## Getting Started

### Prerequisites

- Node.js (v18+)
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *(Ensure `VITE_API_BASE_URL` matches your local running backend port).*

3. Start the local development server:
   ```bash
   npm run dev
   ```
   The application will run on [http://localhost:5173](http://localhost:5173).

### Building for Production

To build the static production files with zero TypeScript errors or unused-import warnings, run:
```bash
npm run build
```
The compiled files will be output to the `dist/` directory.

# Mentesa React Frontend

This is the modern React frontend for Mentesa, replacing the legacy Streamlit app.

## Tech Stack
- React (Vite)
- Tailwind-like styling via standard CSS Variables + Utility classes (Premium Dark Theme)
- React Router v6
- Axios

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run locally:
   ```bash
   npm run dev
   ```

## Build for Production (EC2)

To deploy to your EC2 instance:

1. Build the static files:
   ```bash
   npm run build
   ```
   This creates a `dist` folder containing `index.html` and assets.

2. **Deploying to EC2**:
   - Upload the `dist` folder to your EC2 server (e.g., `/var/www/mentesa`).
   - Configure **Nginx** or **Apache** to serve this folder.
   - Ensure your Nginx config handles client-side routing by redirecting 404s to `index.html`:
     ```nginx
     location / {
         root /var/www/mentesa;
         index index.html;
         try_files $uri $uri/ /index.html;
     }
     ```

## Backend Integration
The app is configured to talk to `https://mentesav8.onrender.com`.
If you change your backend URL, update `src/utils/api.js`.

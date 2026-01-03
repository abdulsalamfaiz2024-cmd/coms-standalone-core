# Deployment Guide

This system is prepared for deployment on **Render** (or any similar PaaS like Heroku/Railway) using **GitHub**.

## 1. Preparation (Already Done)
We have added the following configuration files to your project root:
*   `Procfile`: Tells the server how to start the app.
*   `requirements.txt`: Lists dependencies (none needed for Core).
*   `runtime.txt`: Specifies Python version.
*   `.gitignore`: Prevents temporary files from being uploaded.

## 2. Push to GitHub
1.  Initialize a repository if you haven't (or use your existing one).
2.  Commit all files:
    ```bash
    git add .
    git commit -m "Prepared for Render Deployment"
    git push origin main
    ```

## 3. Deploy on Render
1.  Log in to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **"New +"** -> **"Web Service"**.
3.  Connect your GitHub repository.
4.  Use the following settings:
    *   **Name**: `consultancy-portal` (or your choice)
    *   **Region**: Closest to you (e.g., Frankfurt or Oregon)
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt` (Default is fine)
    *   **Start Command**: `python System_Core/server.py` (Or just let it read the `Procfile`)
    *   **Plan**: `Free`

## 4. Database Note
The system uses a **file-based SQLite database** (`consultancy.db`).
*   **On the Free Tier**: The database will **reset** every time you deploy or if the server restarts (ephemeral storage).
*   **For Review**: This is fine; the system will work, but data created *during* the session might be lost after a while.
*   **Pre-loaded Data**: We have included the current `consultancy.db` in the repository so the reviewer will see your existing data immediately.

## 5. Verification
Once deployed, Render will give you a URL (e.g., `https://consultancy-portal.onrender.com`).
*   Open that URL.
*   The system should load the Login Page or Dashboard.

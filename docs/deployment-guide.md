# Smart Test Selector - Cloud Deployment Guide

Deploy the project to Render.com and get two public HTTPS URLs: one for your metrics api and one for Prometheus dashboards.

---

## Prerequisites

1. Your project must be pushed to GitHub (`git push`).
2. Have a [Render.com](https://render.com) account (free — no credit card required).

---

## STEP 1: Push the new cloud files to GitHub

Open a terminal in your project folder and run:

```bash
git add .
git commit -m "chore: add cloud deployment config for Render.com"
git push
```

---

## STEP 2: Deploy on Render.com

1. Go to **[https://render.com](https://render.com)** and log in.
2. Click **"New +"** in the top right → select **"Blueprint"**.
3. Connect your GitHub account if not already done.
4. Select your repo: **`devops-project-smart-test-selector`**.
5. Render will auto-detect `render.yaml` and list two services:
   - `smart-selector-demo` (your metrics server)
   - `prometheus-server` (monitoring UI)
6. Click **"Apply"**.
7. Wait **3–5 minutes** for both services to build and deploy.

---

## STEP 3: Get your public URLs

After deployment finishes, go to:
- **Dashboard → smart-selector-demo** → copy the public URL (e.g., `https://smart-selector-demo.onrender.com`)
- **Dashboard → prometheus-server** → copy its URL (e.g., `https://prometheus-server.onrender.com`)

**Test your metrics server is live:**
```
https://smart-selector-demo.onrender.com/metrics
```
You should see a page full of Prometheus metric lines!

---

## STEP 4: View live graphs

1. Open `https://prometheus-server.onrender.com` in your browser.
2. Click **Graph** tab.
3. Paste any of these queries and click **Execute**:

| Query | What it shows |
|-------|---------------|
| `smart_tests_run_total` | Total tests run by the CI pipeline |
| `smart_files_changed_current` | Number of changed files per run |
| `rate(smart_tests_run_total[1m])` | Tests processed per minute (throughput) |
| `smart_tests_failed_total` | Total failed tests over time |
| `smart_lint_errors_total` | Total Flake8 linting errors found |

---

## Notes

- The **free tier on Render.com** spins down services after 15 minutes of inactivity. The first request after idle may take 30–60 seconds to wake up.
- To prevent this, bookmark the `/metrics` URL and open it before your presentation to "warm up" the service.
- The Prometheus data **resets on each redeploy** (no persistent storage on free tier), but the demo_mode.py script regenerates data within seconds of startup.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Build failed" on Render | Check that `Dockerfile.demo` exists in root of the repo |
| Prometheus shows no data | Wait 30–60 seconds for first scrape interval, then re-query |
| Metrics page is down / sleeping | Open the Render dashboard and click "Manual Deploy" to wake it |
| Smart-selector URL not found | Confirm the `render.yaml` was pushed to GitHub |

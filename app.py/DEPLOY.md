# Deploy Movie Recommendation App

## Option 1: Streamlit Community Cloud (recommended, free)

1. **Push your project to GitHub**
   - Create a new repository (e.g. `movie-recommendation-app`).
   - Upload your project folder so the repo has:
     - `app1.py`
     - `requirements.txt`
     - `Movie_dict.pkl`
     - `Similarity.pkl`
     - `assests/` (folder with images)

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Sign in with GitHub.
   - Click **"New app"**.
   - Choose your repo and branch.
   - **Main file path:** `app1.py` (or `app.py/app1.py` if the repo root is one level above the folder that contains `app1.py`).
   - Click **Deploy**. Streamlit will install dependencies from `requirements.txt` and run your app.

3. **If your repo structure is**  
   `your-repo / app.py / app1.py`  
   then set **Main file path** to: `app.py/app1.py`.

---

## Option 2: Netlify (not suitable for this app)

Netlify hosts **static sites** (HTML/CSS/JS). This app is a **Streamlit (Python) app** that needs a server. Netlify does not run Streamlit apps.

To use Netlify you would have to:
- Rebuild the UI as a static front end (e.g. React/HTML), and
- Move the recommendation logic to Netlify Functions or another backend.

That’s a full rewrite. For this project, use **Streamlit Community Cloud** instead.

---

---

## Deploy on Render (step-by-step)

### 1. Push your project to GitHub

- Create a repository (e.g. `movie-recommendation-app`).
- **Important:** The **root** of the repo should contain:
  - `app1.py`
  - `requirements.txt`
  - `render.yaml` (included in this folder)
  - `Movie_dict.pkl`
  - `Similarity.pkl`
  - `assests/` (folder with your images)
- Push your code. If your project is under `ml projects/app.py/`, either push **only** the contents of the `app.py` folder as the repo root, or push the whole project and use the path `app.py/app1.py` in step 4.

### 2. Sign up / log in on Render

- Go to **[render.com](https://render.com)**.
- Sign up or log in (GitHub login is easiest).

### 3. Create a new Web Service

- From the **Dashboard**, click **New +** → **Web Service**.
- Connect your GitHub account if needed, then select the repo that contains your app (e.g. `movie-recommendation-app`).
- Click **Connect**.

### 4. Configure the Web Service

- **Root Directory:** Set to **`app.py`** (required). Your `requirements.txt` and `app1.py` are inside this folder; without it, the build runs from the repo root and fails with "Could not open requirements file".
- **Name:** e.g. `movie-recommendation` (or any name you like).
- **Region:** Choose the one closest to you.
- **Branch:** `master` (or the branch you use).
- **Runtime:** **Python 3**.
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run app1.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
- **Instance type:** Free (or paid if you prefer).

### 5. Deploy

- Click **Create Web Service**.
- Render will install dependencies and start the app. The first deploy can take a few minutes.
- When it’s done, you’ll get a URL like `https://movie-recommendation-xxxx.onrender.com`. Open it to use your app.

### 6. (Optional) Use the Blueprint

- If `render.yaml` is in the **root** of your repo, you can use **Blueprint** when creating the service: **New +** → **Blueprint**, select the repo; Render will read `render.yaml` and create the Web Service with the right build and start commands.

### Notes

- **Free tier:** The service may spin down after 15 minutes of no use; the next visit can take 30–60 seconds to wake up.
- **Files:** `Movie_dict.pkl`, `Similarity.pkl`, and the `assests/` folder must be in the repo (and in the same path your app expects), or the app will fail at runtime.

### Troubleshooting: "Connection failed with status 503"

**1. Cold start (most common)**  
On the free tier, the app **sleeps** after ~15 minutes of no traffic. The first request after that can return **503** while the server is waking up.  
- **Fix:** Wait **30–60 seconds** and **refresh** the page. Avoid closing the tab as soon as you see 503.

**2. Check Render logs**  
- In the Render dashboard, open your **Web Service** → **Logs** (and **Events**) tab.  
- Look for **"Your service is live"** (startup succeeded) or errors like **"Killed"**, **"Out of memory"**, **"ModuleNotFoundError"**, or **"FileNotFoundError"**.  
- If you see **Out of memory** or **Killed**: the free instance (512 MB RAM) may be too small for loading `Similarity.pkl` (~176 MB) plus Streamlit.  
  - **Fix:** Upgrade to a **paid instance** (e.g. 512 MB → 1 GB+) on Render, or deploy on **Streamlit Community Cloud** (often more generous for this kind of app).

**3. Build / start command**  
- Ensure **Root Directory** is empty (or set to `app.py` if you use that as root).  
- Build: `cd app.py && pip install -r requirements.txt`  
- Start: `cd app.py && streamlit run app1.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

**4. Git LFS**  
- Render’s build image does **not** include Git LFS, so do **not** put `git lfs pull` in the Build Command (you’ll get “git: 'lfs' is not a git command”). Render fetches LFS files during **clone** by default, so use Build Command: `pip install -r requirements.txt` only. If the app later fails to find `Similarity.pkl`, the LFS file may not have been pulled; in that case consider hosting the file elsewhere or using another platform (e.g. Streamlit Community Cloud).

**5. Build failed: "Exited with status 1" / Python 3.14**  
- Render may use Python 3.14 by default; Streamlit and other deps often don’t support it yet. Pin the runtime: add a **`runtime.txt`** at your **repo root** (same level as the `app.py` folder) with:
  ```
  python-3.11.7
  ```
  Commit, push, and redeploy. If your Render **Root Directory** is set to `app.py`, put `runtime.txt` inside `app.py` instead.

---

## Option 3: Other platforms that run Streamlit

- **Railway** – [railway.app](https://railway.app) – Add a Procfile: `web: streamlit run app1.py --server.port=$PORT`
- **Hugging Face Spaces** – [huggingface.co/spaces](https://huggingface.co/spaces) – Supports Streamlit; add `requirements.txt` and your files.

For the least setup, use **Streamlit Community Cloud**.

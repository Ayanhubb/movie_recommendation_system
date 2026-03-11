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

- **Name:** e.g. `movie-recommendation` (or any name you like).
- **Region:** Choose the one closest to you.
- **Branch:** `main` (or the branch you use).
- **Runtime:** **Python 3**.
- **Build Command:**  
  `pip install -r requirements.txt`  
  (If your files are in a subfolder, e.g. `app.py/`, use:  
  `cd app.py && pip install -r requirements.txt`)
- **Start Command:**  
  `streamlit run app1.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`  
  (If your app is in a subfolder:  
  `cd app.py && streamlit run app1.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`)
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

---

## Option 3: Other platforms that run Streamlit

- **Railway** – [railway.app](https://railway.app) – Add a Procfile: `web: streamlit run app1.py --server.port=$PORT`
- **Hugging Face Spaces** – [huggingface.co/spaces](https://huggingface.co/spaces) – Supports Streamlit; add `requirements.txt` and your files.

For the least setup, use **Streamlit Community Cloud**.

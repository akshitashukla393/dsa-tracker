# 🚀 DSA Tracker – Interactive Problem Tracker with GitHub Sync

Track your DSA progress visually, manage your solved problems and automatically back them up to GitHub. Built with a sleek frontend and a Flask backend.

---

## 📁 Project Structure

```
frontend/
├── static/
│   ├── index.html      # Main user interface
│   ├── styles.css      # Clean, modern teal-themed styling
│   └── script.js       # Handles frontend logic and API calls
├── app.py              # Flask backend (serves API + frontend)
├── data/               # Auto-generated for local storage (problems.json, config.json)
```

---

## ⚙️ How to Run the Application

### 1. 📥 Clone the Repository

```bash
git clone https://github.com/akshitashukla393/dsa-tracker.git
cd dsa-tracker/frontend
```

### 2. 📦 Install Dependencies

Make sure Python 3 is installed, then install required packages:

```bash
pip install flask flask-cors requests
```

### 3. ▶️ Run the Flask Server

```bash
python app.py
```

You’ll see output like:

```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.x:5000
```

> Open [http://127.0.0.1:5000] in your browser to use the app.

---

## 🌟 Features

- ✅ Add, filter, and delete DSA problems
- 📊 Track stats by difficulty, platform, and category
- 🔍 Search problems dynamically
- 📁 Export or import problem data as JSON
- ☁️ Sync all data to a GitHub repo automatically
- 🎨 Responsive and elegant teal-colored UI

---

## 🔐 GitHub Sync Setup

To enable syncing your data to GitHub, follow the steps below.

### Step 1: Generate a GitHub Personal Access Token (Classic)

1. Visit [https://github.com/settings]
2. Go to Developer settings and go to Personal access tokens
2. Click **Generate new token (classic)**
3. Give it a name (e.g., `DSA Tracker Sync Token`)
4. Set expiration as desired
5. Check the following scopes:
   - ✅ `repo` – Full control of private repositories
6. Click **Generate token** and copy it immediately

> ⚠️ This token is like a password — never share it publicly.

### Step 2: Use the Token in the App

1. In the **GitHub Sync** section of the app:
   - Enter your **GitHub username**
   - Paste the **token**
   - Enter the **repository name** (e.g., `dsa-tracker-data`)
2. Click **Setup GitHub**
3. Then click **Sync to GitHub**

✔️ The app will:
- Create the repo automatically (if it doesn’t exist)
- Upload your data as `README.md` and `problems.json`

---

## 📦 Example Problem (After Sync)

```json
{
  "id": 1,
      "name": "Two Sum",
      "platform": "LeetCode",
      "difficulty": "easy",
      "category": "Two Pointers",
      "status": "solved",
      "date_solved": "2025-07-23T11:43:21.429173",
      "solution_path": null,
      "notes": "",
      "attempts": 1
}
```

---

# StockLens — SETUP.md

**Purpose:** Complete installation and setup guide to get StockLens running locally from scratch. Written from what was actually verified working on Day 3 (Windows 11, Python 3.12.8).

---

## Prerequisites

| Tool | Version confirmed | Purpose |
|---|---|---|
| Python | 3.12.8 | Runs the Flask backend |
| pip | 24.3.1 (bundled with Python) | Installs Python packages |
| VS Code | Latest | Code editor with Python support |
| VS Code Python Extension | Microsoft's official extension | IntelliSense, run/debug support |
| Git | Bundled with Git for Windows install | Version control |
| Git GUI | Bundled with Git for Windows | Beginner-friendly clone/commit interface |

---

## Windows-Specific Notes (encountered and resolved on Day 3)

### Issue 1: `pip` blocked by Device Guard
On managed/institutional Windows laptops, `pip.exe` may be blocked directly by a security policy called Device Guard, showing:
```
'...\pip.exe' was blocked by your organization's Device Guard policy.
```
**Fix:** Always run pip through Python itself instead of standalone:
```
python -m pip install <package>
python -m pip freeze
```
This works because `python.exe` is trusted even when `pip.exe` alone is blocked.

### Issue 2: PowerShell blocks virtual environment activation
When running `.\venv\Scripts\Activate.ps1`, PowerShell may show:
```
running scripts is disabled on this system
```
**Fix (one-time, per user account):**
```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Confirm with `Y` if prompted, then re-run the activation command.

---

## Step-by-Step Local Setup

1. **Clone the repository** (already done Day 2):
   ```
   git clone https://github.com/rahulmayur95-cyber/Stock-Lens.git
   ```

2. **Open the project in VS Code:** File → Open Folder → select the `stock-Lens` folder.

3. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

4. **Activate the virtual environment (Windows / PowerShell):**
   ```
   .\venv\Scripts\Activate.ps1
   ```
   You should see `(venv)` appear at the start of your terminal prompt.
   > Re-run this activation command every time you open a new terminal for this project.

5. **Install dependencies:**
   ```
   python -m pip install flask requests python-dotenv
   ```

6. **Freeze exact versions into requirements.txt** (already done Day 3, re-run if new packages are added):
   ```
   python -m pip freeze > requirements.txt
   ```

7. **Set up environment variables:**
   - Copy `.env.example` to a new file named `.env` (same folder).
   - Fill in your real values:
     ```
     FINNHUB_API_KEY=your_real_finnhub_key
     FLASK_SECRET_KEY=any_long_random_string
     ```
   - Get a free Finnhub API key at https://finnhub.io/register (see ENVIRONMENT.md for details).
   - `.env` is git-ignored and must never be committed.

8. **Run the app:**
   ```
   python app.py
   ```
   On first run, this automatically creates `stocklens.db` from `schema.sql`.

9. **Verify it's working:** open a browser to `http://127.0.0.1:5000` — you should see "StockLens is running."

10. **Stop the server** anytime with `Ctrl + C` in the terminal.

---

## Verifying Everything Works (Day 3 Checklist)

- [ ] `python app.py` starts with no errors
- [ ] Terminal shows `Database initialized from schema.sql` on first run
- [ ] `http://127.0.0.1:5000` shows "StockLens is running"
- [ ] `http://127.0.0.1:5000/dashboard` redirects back to `/` (auth scaffold working, since no login exists yet)
- [ ] `stocklens.db` file appears in the project folder after first run

---

## Common Issues & Fixes

| Problem | Likely Cause | Fix |
|---|---|---|
| `pip` "blocked by Device Guard" | Institutional security policy | Use `python -m pip ...` instead of `pip ...` |
| "running scripts is disabled" on activation | PowerShell default execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `ModuleNotFoundError: No module named 'flask'` | Virtual environment not activated | Run `.\venv\Scripts\Activate.ps1` before `python app.py` |
| App can't find `FLASK_SECRET_KEY` | `.env` missing or not in project root | Confirm `.env` exists in the same folder as `app.py`, not inside a subfolder |
| `git status` says "not a git repository" | Terminal is one folder level too high | `cd` into the actual cloned folder (e.g., `cd "stock-Lens"`) |

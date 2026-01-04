# Goal Bubbles App

A Dash-based web application that visualizes goals as colorful bubbles. Goals can be filtered, searched, updated, and added through the UI. The app ships with a curated set of professional and personal goals.

## Setup
1. Ensure Python 3.11+ is available.
2. (Optional) Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the app
Start the Dash development server:
```bash
python app.py
```
The app will be available at `http://127.0.0.1:8050`.

### Interacting with the UI
- **Update status + recolor**: pick a bubble in the “Update goal status” panel, add a progress/status note, and click **Update status**. Each save shifts the bubble to a new palette color.
- **Add goals**: use the Add form to add your own goal with a category and horizon.
- **Sync to Firebase**: provide a Firebase Realtime Database URL (ending in `.json`) or a Firestore REST endpoint and click **Sync to Firebase**. Include an auth token if your Firebase rules require it.

## Tests
A quick syntax check is available:
```bash
python -m py_compile app.py
```

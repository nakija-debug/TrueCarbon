# Backend skeleton for TRUE CARBON

This folder contains a minimal FastAPI-based backend skeleton with comments that explain where to hook up authentication (fastapi-users) and the database.

How to run (development):

1. Create a virtualenv and install requirements:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn main:app --reload
```

Notes for integration:
- The frontend sends POST to `/auth/jwt/login` and `/auth/register` (examples in `login/auth.js`).
- This skeleton does not implement full fastapi-users wiring; it provides placeholders and guidance.

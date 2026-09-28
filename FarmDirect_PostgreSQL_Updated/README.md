# FarmDirect - BCA Mini Project (PostgreSQL)

FarmDirect connects farmers directly with buyers and provides a simple crop-price suggestion feature.

## Features
- Farmer registration/login
- Buyer registration/login
- Admin dashboard
- Farmer crop listing
- Crop search
- Direct purchase requests
- Farmer order accept/reject
- Price suggestion from stored market-price history
- PostgreSQL database
- Responsive Bootstrap UI

## Project structure
```text
FarmDirect_PostgreSQL_Updated/
├── app.py
├── requirements.txt
├── schema_postgres.sql
├── .env.example
├── .gitignore
├── README.md
├── templates/
└── static/
```

## Render deployment
1. Create a Render PostgreSQL database, for example `farmdirect-db`.
2. Keep the PostgreSQL database and FarmDirect web service in the same Render region.
3. Open the PostgreSQL database and choose **Connect**.
4. Copy the **Internal Database URL**. Do not put it in GitHub.
5. Open the FarmDirect Web Service → **Environment**.
6. Add:
   - Key: `DATABASE_URL`
   - Value: your Render Internal Database URL
7. Add a `SECRET_KEY` environment variable with a random secret value.
8. Build Command:
   `pip install -r requirements.txt`
9. Start Command:
   `gunicorn app:app`
10. Deploy the service.
11. Load `schema_postgres.sql` into the Render PostgreSQL database before testing registration, crop listings, orders, or price suggestions.

## Local development
A local PostgreSQL server is optional. If you do not have PostgreSQL installed/running locally, do not use `http://127.0.0.1:5000` expecting it to use the Render database unless you set `DATABASE_URL` to a valid connection URL.

For local PostgreSQL, create a database named `farmdirect`, run `schema_postgres.sql`, then set the DB_* variables from `.env.example` in your terminal and run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

## GitHub
Commit and push the project files. Never commit `.env` or a real database URL/password.

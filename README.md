# Sales Management System (Flask + PostgreSQL)

Simple, production-ready Sales Management System 

## Features
- Auth: register/login/logout
- Products: full CRUD (name, SKU, price, stock)
- Sales: record sale (product, quantity, unit price, date) + list/delete
- Dashboard: total revenue, total sales count, product count

## Project structure
- `app.py` – Flask app factory + entrypoint
- `models.py` – SQLAlchemy models (User/Product/Sale)
- `routes/` – blueprints (auth, dashboard, products, sales)
- `templates/` – Bootstrap UI
- `static/` – CSS

## Database schema (PostgreSQL)
Tables:
- `users`: `id`, `username`, `email`, `password_hash`, `created_at`
- `products`: `id`, `name`, `sku`, `price`, `stock`, `created_at`
- `sales`: `id`, `product_id`, `user_id`, `quantity`, `unit_price`, `sale_date`, `created_at`

Notes:
- `products.name` is unique; `products.sku` is optional but unique if provided.
- Recording a sale decrements `products.stock`. Deleting a sale restores it.

## Environment variables
Required:
- `SECRET_KEY`
- `DATABASE_URL`

Optional:
- `PORT` (Railway sets this automatically)
- `LOG_LEVEL` (default `INFO`)
- `AUTO_MIGRATE=1` (dev convenience: calls `db.create_all()` on startup)

See `.env.example`.

## Local setup (Postgres)
1) Create and activate a virtualenv
2) Install deps: `pip install -r requirements.txt`
3) Create `.env` from `.env.example` and update values
4) Run: `python app.py`
5) Open: `http://127.0.0.1:5000`

### Migrations (recommended for production)
This project includes Flask-Migrate.

Commands:
- `flask --app app.py db init`
- `flask --app app.py db migrate -m "init"`
- `flask --app app.py db upgrade`

## Endpoints (server-rendered)
- `GET /` Dashboard (login required)
- `GET /auth/login`, `POST /auth/login`
- `GET /auth/register`, `POST /auth/register`
- `POST /auth/logout`
- `GET /products/`, `GET/POST /products/new`, `GET/POST /products/<id>/edit`, `POST /products/<id>/delete`
- `GET /sales/`, `GET/POST /sales/new`, `POST /sales/<id>/delete`
- `GET /health` Health check JSON

## Example database records (sample)
Users:
- username: `alice`, email: `alice@example.com`

Products:
- `Laptop`, sku `LAP-001`, price `1200.00`, stock `10`
- `Mouse`, sku `MOU-010`, price `20.00`, stock `100`

Sales:
- product `Laptop`, qty `1`, unit_price `1200.00`, date `2026-04-03`
- product `Mouse`, qty `2`, unit_price `18.50`, date `2026-04-03`

## Railway deployment (GitHub → Railway auto-deploy)
1) Push to GitHub:
- `git init`
- `git add .`
- `git commit -m "Initial commit"`
- Create a GitHub repo and push it (`git remote add origin ...`, `git push -u origin main`)

2) Create Railway project:
- Railway → New Project → Deploy from GitHub Repo

3) Add a PostgreSQL database:
- Railway → Add → Database → PostgreSQL

4) Set Railway Variables (Web service → Variables):
- `DATABASE_URL` (ensure the Postgres service variable is available to the web service)
- `SECRET_KEY` (generate a strong random value)

5) Deploy:
- Railway uses `Procfile`: `web: gunicorn wsgi:app --bind 0.0.0.0:${PORT}`
- App binds to `0.0.0.0` and `PORT`

### CI/CD (auto-deploy on push)
- Railway redeploys automatically when you push to the connected branch.
- Optional: enable branch protection rules on GitHub for safer deployments.

## Logging & debugging
Common issues:
1) Database connection failure
   - Error examples: `psycopg2.OperationalError`, timeouts, “could not translate host name”
   - Fix: confirm `DATABASE_URL` is set for the web service; verify Postgres is running and accessible.
   - Action: open Railway Logs; look for the first exception stack trace.
2) Missing environment variables
   - If `SECRET_KEY` is missing: logins may work inconsistently and sessions will break on restart.
   - If `DATABASE_URL` is missing: pages will error when they access the DB.
   - Fix: set both variables in Railway → Variables and redeploy.

## Scalability considerations (short + practical)
- The app is stateless (cookie sessions). Railway can run multiple instances (“replicas”) behind its routing layer.
- The database is the primary bottleneck; add indexes, paginate lists, and avoid expensive dashboard aggregates.
- Railway scaling basics:
  - Horizontal: increase replicas of the web service (more concurrent requests).
  - Vertical: increase RAM/CPU for the service (fewer timeouts under load).
  - Watch Postgres connection limits when scaling web replicas (use pooling if needed).
- Improvements for larger traffic:
  - Add Redis caching for dashboard totals
  - Add pagination/search for products and sales
  - Add async/background jobs for reports

## Testing
Run:
- `pytest -q`

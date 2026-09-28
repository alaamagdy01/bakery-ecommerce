# 🍪 Sweet Crumb Bakery - AI-Powered E-Commerce System

A web-based bakery e-commerce platform (cookies, cakes, donuts, cupcakes,
pastries, breads) with an AI-powered recommendation engine, built to the same
specification as the provided SRS.

**Stack:** Django (Python) · PostgreSQL · HTML/CSS/Vanilla JavaScript
(no frontend frameworks, per project constraints).

---

## 1. Features

| SRS Requirement | Implementation |
|---|---|
| FR-1 Authentication | Register / Login / Logout (`accounts` app) |
| FR-2 Product Management | Admin dashboard: add/edit/delete/view products (`products` app) + Django admin |
| FR-3 Product Browsing | Home page, search, category filter, price filter, sorting, pagination |
| FR-4 Shopping Cart | Add/update/remove items, persistent per-user cart, AJAX add-to-cart |
| FR-5 Order Management | Checkout, order history, admin order list & status updates |
| FR-6 AI Recommendations | Similar products, trending products, personalized picks - each with a generated explanation |

### AI Recommendation Assistant (Section 4 of the SRS)
Implemented in `recommendations/services.py` as an explainable,
data-driven engine (no external ML service required):
- **Similar products** - content-based filtering by shared category + ingredients.
- **Trending products** - ranks products by units sold in the last 30 days, with a graceful fallback to featured/newest items for a fresh store.
- **Personalized picks** - looks at a customer's most-viewed category and recommends unpurchased items from it.
- **Explanation generation** - every recommendation returns a short, human-readable reason (e.g. *"Trending now - 42 sold in the last 30 days."*).

These are exposed as JSON endpoints (see `docs/API_DOCUMENTATION.md`) and
rendered by vanilla JavaScript widgets on the home page and product detail
page.

---

## 2. Project Structure

```
bakery_ecommerce/
├── config/                # Django project settings, root URLs
├── accounts/              # Registration, login, logout, profile
├── products/              # Categories, products, browsing, admin CRUD
├── cart/                  # Shopping cart
├── orders/                # Checkout, order history, admin order management
├── recommendations/       # AI recommendation engine + JSON API
├── templates/             # Shared templates (base.html, navbar)
├── static/                # CSS & vanilla JS
├── docs/                  # API docs + ER diagram
├── requirements.txt
├── manage.py
└── .env.example
```

---

## 3. Setup Instructions

### 3.1 Prerequisites
- Python 3.11+
- PostgreSQL 14+ running locally (or accessible remotely)

### 3.2 Installation

```bash
# 1. Clone / unzip the project, then enter the folder
cd bakery_ecommerce

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# edit .env with your PostgreSQL credentials and a real SECRET_KEY

# 5. Create the PostgreSQL database (example using psql)
psql -U postgres -c "CREATE DATABASE bakery_db;"
psql -U postgres -c "CREATE USER bakery_user WITH PASSWORD 'bakery_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bakery_db TO bakery_user;"

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create an admin/superuser account
python manage.py createsuperuser

# 8. Seed sample bakery products (cookies, cakes, donuts...)
python manage.py seed_bakery

# 9. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the storefront and
`http://127.0.0.1:8000/admin/` for the full Django admin.

### 3.3 Making a customer an "admin/staff" without full superuser rights
In the Django admin, open **Profiles** and tick **is_admin_staff** on that
user's profile - they will then be able to access `/dashboard/products/` and
`/orders/dashboard/orders/` to manage products and orders.

---

## 4. Deliverables Checklist

- ✅ Complete source code (this repository)
- ✅ API documentation → `docs/API_DOCUMENTATION.md`
- ✅ ER Diagram → `docs/ER_diagram.png` (image) and `docs/ER_DIAGRAM.md` (Mermaid source)
- ⬜ Demo — record a short walkthrough after running the steps above (register → browse → add to cart → checkout → view AI recommendations → admin manages products/orders)

---

## 5. Non-Functional Notes

- Forms validate input server-side (e.g. price/stock cannot be negative, phone number format, stock availability at checkout) with meaningful inline error messages.
- Permission checks redirect unauthorized users to login rather than raising raw errors.
- Code is organized into small, single-responsibility Django apps (`accounts`, `products`, `cart`, `orders`, `recommendations`) following Django best practices (forms, class-free function-based views kept thin, business logic isolated in `recommendations/services.py`).

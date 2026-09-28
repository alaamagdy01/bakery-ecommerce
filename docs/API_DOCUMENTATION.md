# Sweet Crumb Bakery - API & Endpoint Documentation

The system is primarily server-rendered (Django templates + vanilla JS), per the
project's technology constraints. The endpoints below marked **JSON API** are
consumed by vanilla JavaScript (`fetch`) for the AI recommendation widgets and
the "Add to Cart" action. All other endpoints are standard Django views that
render HTML pages and process form submissions.

Base URL (local development): `http://127.0.0.1:8000`

---

## Authentication (FR-1)

| Method | URL | Description | Auth |
|---|---|---|---|
| GET/POST | `/accounts/register/` | Customer registration form | Public |
| GET/POST | `/accounts/login/` | Login form | Public |
| GET/POST | `/accounts/logout/` | Log out current user | Logged in |
| GET/POST | `/accounts/profile/` | View/update phone & address | Logged in |

## Product Browsing (FR-3)

| Method | URL | Description | Auth |
|---|---|---|---|
| GET | `/` | Home page: featured, trending & personalized picks | Public |
| GET | `/products/` | Browse/search/filter products. Query params: `q`, `category`, `min_price`, `max_price`, `sort`, `page` | Public |
| GET | `/products/category/<slug>/` | Products filtered by category | Public |
| GET | `/products/<slug>/` | Product detail page | Public |

## Product Management - Admin (FR-2)

| Method | URL | Description | Auth |
|---|---|---|---|
| GET | `/dashboard/products/` | List all products for management | Staff/Admin |
| GET/POST | `/dashboard/products/add/` | Add a new product | Staff/Admin |
| GET/POST | `/dashboard/products/<slug>/edit/` | Edit a product | Staff/Admin |
| GET/POST | `/dashboard/products/<slug>/delete/` | Delete a product (confirmation page) | Staff/Admin |
| — | `/admin/` | Full Django admin (products, categories, orders, users) | Superuser |

## Shopping Cart (FR-4)

| Method | URL | Description | Auth |
|---|---|---|---|
| GET | `/cart/` | View current cart | Logged in |
| POST | `/cart/add/<product_id>/` | Add product to cart. Body: `quantity`. Returns JSON if called via `fetch` (`X-Requested-With: XMLHttpRequest`), otherwise redirects. | Logged in |
| POST | `/cart/update/<item_id>/` | Update quantity of a cart item. Body: `quantity` | Logged in |
| POST | `/cart/remove/<item_id>/` | Remove an item from the cart | Logged in |

**Add to cart - JSON response example**
```json
{
  "success": true,
  "message": "Chocolate Chip Cookie added to your cart.",
  "cart_total_items": 3,
  "cart_total_price": "10.75"
}
```

## Order Management (FR-5)

| Method | URL | Description | Auth |
|---|---|---|---|
| GET/POST | `/orders/checkout/` | Place an order from the current cart | Logged in |
| GET | `/orders/history/` | Customer's own order history | Logged in |
| GET | `/orders/<order_id>/` | Order detail (owner or staff) | Logged in |
| GET | `/orders/dashboard/orders/` | Admin: list all orders. Query param: `status` | Staff/Admin |
| GET/POST | `/orders/dashboard/orders/<order_id>/update/` | Admin: update order status | Staff/Admin |

Order statuses: `pending`, `confirmed`, `baking`, `ready`, `completed`, `cancelled`.

## AI Product Recommendations (FR-6) - JSON API

These are the endpoints called by vanilla JavaScript to power the "You Might
Also Like", "Trending Now" and "Recommended For You" widgets.

### `GET /api/recommendations/similar/<product_id>/`
Content-based recommendation: products sharing the same category and/or
ingredients as the given product.

Query params: `limit` (default 4)

```json
{
  "product_id": 12,
  "results": [
    {
      "id": 5,
      "name": "Double Chocolate Cookie",
      "slug": "double-chocolate-cookie",
      "price": "3.75",
      "category": "Cookies",
      "image_url": null,
      "url": "/products/double-chocolate-cookie/",
      "score": 3,
      "explanation": "Recommended because it's also in Cookies, shares chocolate chips as Chocolate Chip Cookie."
    }
  ]
}
```

### `GET /api/recommendations/trending/`
Products with the most units sold in the last 30 days (falls back to
featured/newest products when order history is sparse).

Query params: `limit` (default 6)

```json
{
  "results": [
    {
      "id": 3,
      "name": "Glazed Donut",
      "price": "2.25",
      "category": "Donuts",
      "score": 42,
      "explanation": "Trending now - 42 sold in the last 30 days."
    }
  ]
}
```

### `GET /api/recommendations/for-you/`
Personalized picks based on the logged-in customer's browsing history
(favourite category), excluding items already ordered. Requires login;
returns an empty list with a `detail` message if the user is anonymous.

Query params: `limit` (default 6)

---

## Error Handling

- Invalid form submissions re-render the form with field-level `errorlist`
  messages (e.g. negative price/stock, insufficient stock at checkout).
- Permission-protected views (`/dashboard/...`, `/orders/dashboard/...`)
  redirect anonymous or non-staff users to `/accounts/login/`.
- The cart "Add to Cart" JSON endpoint returns HTTP 400 with
  `{"success": false, "error": "..."}` when requested quantity exceeds stock.
- All list views (`/products/`) return a friendly empty state instead of an
  error when no results match the filters.

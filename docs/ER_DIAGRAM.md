# ER Diagram - Sweet Crumb Bakery E-Commerce System

A rendered image is available at `docs/ER_diagram.png`. The Mermaid source
below is provided as an editable, text-based alternative (renders on GitHub
and most Markdown viewers that support Mermaid).

```mermaid
erDiagram
    USER ||--|| PROFILE : has
    USER ||--|| CART : owns
    USER ||--o{ ORDER : places
    USER ||--o{ PRODUCTVIEW : generates
    CATEGORY ||--o{ PRODUCT : contains
    PRODUCT ||--o{ PRODUCTVIEW : "viewed in"
    PRODUCT ||--o{ CARTITEM : "added as"
    PRODUCT ||--o{ ORDERITEM : "ordered as"
    CART ||--o{ CARTITEM : contains
    ORDER ||--o{ ORDERITEM : contains

    USER {
        int id PK
        string username
        string email
        string password
    }
    PROFILE {
        int id PK
        int user_id FK
        string phone_number
        string address
        bool is_admin_staff
    }
    CATEGORY {
        int id PK
        string name
        string slug
        text description
    }
    PRODUCT {
        int id PK
        int category_id FK
        string name
        string slug
        text description
        string ingredients
        decimal price
        int stock
        string image
        bool is_available
        bool is_featured
        int created_by FK
    }
    PRODUCTVIEW {
        int id PK
        int user_id FK
        int product_id FK
        datetime viewed_at
    }
    CART {
        int id PK
        int user_id FK
    }
    CARTITEM {
        int id PK
        int cart_id FK
        int product_id FK
        int quantity
    }
    ORDER {
        int id PK
        int user_id FK
        string status
        string delivery_address
        string phone_number
        text notes
        decimal total_price
        datetime created_at
    }
    ORDERITEM {
        int id PK
        int order_id FK
        int product_id FK
        string product_name
        decimal unit_price
        int quantity
    }
```

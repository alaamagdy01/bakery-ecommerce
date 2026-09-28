/* Sweet Crumb Bakery - vanilla JavaScript only (no frameworks, per project constraints) */

function getCsrfToken() {
    return window.CSRF_TOKEN || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
}

function showFlash(message, type) {
    const container = document.querySelector('.messages') || (() => {
        const div = document.createElement('div');
        div.className = 'messages';
        document.querySelector('main.container').prepend(div);
        return div;
    })();
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'error' : 'success'}`;
    alert.textContent = message;
    container.prepend(alert);
    setTimeout(() => alert.remove(), 4000);
}

/**
 * FR-4: Add a product to the cart via fetch() (AJAX), without a full page reload.
 * Falls back gracefully - the surrounding <form> still works with plain POST
 * if JavaScript is disabled.
 */
function initAddToCartForms() {
    document.querySelectorAll('form.add-to-cart-form').forEach((form) => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const url = form.getAttribute('action');
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        showFlash(data.message, 'success');
                        const badge = document.getElementById('cart-badge');
                        if (badge) badge.textContent = data.cart_total_items;
                    } else {
                        showFlash(data.error || 'Could not add product to cart.', 'error');
                    }
                })
                .catch(() => showFlash('Something went wrong. Please try again.', 'error'));
        });
    });
}

/**
 * FR-6: AI recommendation widgets.
 * Fetches JSON from the recommendation API and renders a small product grid,
 * including the AI-generated explanation for each suggestion.
 */
function renderRecommendationCards(container, products) {
    container.innerHTML = '';
    if (!products.length) {
        container.innerHTML = '<p class="empty-state">No recommendations available yet.</p>';
        return;
    }
    products.forEach((product) => {
        const card = document.createElement('a');
        card.href = product.url;
        card.className = 'product-card';
        card.innerHTML = `
            ${product.image_url
                ? `<img src="${product.image_url}" alt="${product.name}">`
                : `<div class="placeholder-img">🍰</div>`}
            <div class="product-card-body">
                <span class="badge-ai">AI Pick</span>
                <span class="category-tag">${product.category}</span>
                <h3>${product.name}</h3>
                <div class="price">$${product.price}</div>
                <div class="ai-explanation">${product.explanation}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

function loadRecommendations(container) {
    const endpoint = container.dataset.endpoint;
    if (!endpoint) return;

    fetch(endpoint, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then((response) => response.json())
        .then((data) => renderRecommendationCards(container, data.results || []))
        .catch(() => {
            container.innerHTML = '<p class="empty-state">Recommendations are unavailable right now.</p>';
        });
}

function initRecommendationWidgets() {
    document.querySelectorAll('[data-recommendation-widget]').forEach(loadRecommendations);
}

document.addEventListener('DOMContentLoaded', () => {
    initAddToCartForms();
    initRecommendationWidgets();
});

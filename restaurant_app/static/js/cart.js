/**
 * Smart Restaurant Food Ordering - Dynamic Cart & Menu Filter System
 * Handles localStorage persistence, quantity calculations, category filtering,
 * search, dietary toggles, and seamless checkout workflow.
 */

// Cart storage key
const STORAGE_KEY = 'smart_restaurant_cart';

// State management
let cartState = {};

// Initialize cart from localStorage on page load
function initCart() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            cartState = JSON.parse(stored);
        }
    } catch (e) {
        console.error('Failed to load cart from storage', e);
        cartState = {};
    }
    renderCart();
    updateNavBadge();
}

// Save cart state to localStorage
function saveCart() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cartState));
    } catch (e) {
        console.error('Failed to persist cart to storage', e);
    }
    updateNavBadge();
}

// Format numbers as currency
function formatINR(amount) {
    return '₹' + Number(amount).toFixed(2);
}

// Add item to cart
function addToCart(id, name, price, isVeg) {
    const key = String(id);
    if (cartState[key]) {
        if (cartState[key].quantity < 50) {
            cartState[key].quantity += 1;
        } else {
            showToast('Maximum quantity of 50 reached for this item.', 'warning');
            return;
        }
    } else {
        cartState[key] = {
            id: Number(id),
            name: String(name),
            price: Number(price),
            isVeg: Boolean(isVeg),
            quantity: 1
        };
    }

    saveCart();
    renderCart();
    showToast(`Added <strong>${name}</strong> to your cart! 🛒`, 'success');

    // Trigger subtle button bounce if item card is present
    const btn = document.getElementById(`addBtn_${id}`);
    if (btn) {
        btn.classList.add('btn-bounce');
        setTimeout(() => btn.classList.remove('btn-bounce'), 300);
    }
}

// Update item quantity
function updateQuantity(id, delta) {
    const key = String(id);
    if (!cartState[key]) return;

    cartState[key].quantity += delta;
    if (cartState[key].quantity <= 0) {
        delete cartState[key];
        showToast('Item removed from cart.', 'info');
    }

    saveCart();
    renderCart();
}

// Remove item entirely from cart
function removeFromCart(id) {
    const key = String(id);
    if (cartState[key]) {
        delete cartState[key];
        saveCart();
        renderCart();
        showToast('Item removed from cart.', 'info');
    }
}

// Clear entire cart
function clearCart() {
    if (Object.keys(cartState).length === 0) return;
    if (confirm('Are you sure you want to clear your entire cart?')) {
        cartState = {};
        saveCart();
        renderCart();
        showToast('Cart cleared.', 'info');
    }
}

// Update navbar cart item counter
function updateNavBadge() {
    const count = Object.values(cartState).reduce((acc, item) => acc + item.quantity, 0);
    const badges = document.querySelectorAll('.cart-counter-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    });

    const mobileCount = document.getElementById('mobileCartCount');
    if (mobileCount) mobileCount.textContent = count;
}

// Render cart items, calculations (Subtotal, 5% Tax, Grand Total)
function renderCart() {
    const container = document.getElementById('cartItemsList');
    const emptyState = document.getElementById('cartEmptyState');
    const checkoutBtn = document.getElementById('placeOrderButton');
    const cartSummaryBox = document.getElementById('cartSummaryBox');

    const items = Object.values(cartState);

    if (items.length === 0) {
        if (container) container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        if (cartSummaryBox) cartSummaryBox.style.display = 'none';
        if (checkoutBtn) checkoutBtn.disabled = true;

        updateCalculations(0, 0, 0);
        syncCartInput();
        return;
    }

    if (emptyState) emptyState.style.display = 'none';
    if (cartSummaryBox) cartSummaryBox.style.display = 'block';
    if (checkoutBtn) checkoutBtn.disabled = false;

    let subtotal = 0;
    let html = '';

    items.forEach(item => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;

        const vegIcon = item.isVeg ? '<span class="text-success me-1">🟢</span>' : '<span class="text-danger me-1">🔴</span>';

        html += `
        <div class="cart-item-row">
            <div style="flex: 1; padding-right: 12px;">
                <div class="cart-item-name">${vegIcon} ${item.name}</div>
                <div class="text-muted small">${formatINR(item.price)} each</div>
            </div>
            <div class="qty-control me-3">
                <button type="button" class="qty-btn" onclick="updateQuantity(${item.id}, -1)" title="Decrease quantity">−</button>
                <span class="qty-number">${item.quantity}</span>
                <button type="button" class="qty-btn" onclick="updateQuantity(${item.id}, 1)" title="Increase quantity">+</button>
            </div>
            <div class="text-end" style="min-width: 75px;">
                <div class="fw-bold">${formatINR(itemTotal)}</div>
                <button type="button" class="btn btn-link text-danger p-0 small" onclick="removeFromCart(${item.id})" style="font-size: 0.75rem; text-decoration: none;">Remove</button>
            </div>
        </div>
        `;
    });

    if (container) container.innerHTML = html;

    // 5% GST/Tax calculation
    const tax = Math.round(subtotal * 0.05 * 100) / 100;
    const grandTotal = subtotal + tax;

    updateCalculations(subtotal, tax, grandTotal);
    syncCartInput();
}

function updateCalculations(subtotal, tax, grandTotal) {
    const elSub = document.getElementById('cartSubtotal');
    const elTax = document.getElementById('cartTax');
    const elGrand = document.getElementById('cartGrandTotal');
    const elMobileGrand = document.getElementById('mobileCartTotal');

    if (elSub) elSub.textContent = formatINR(subtotal);
    if (elTax) elTax.textContent = formatINR(tax);
    if (elGrand) elGrand.textContent = formatINR(grandTotal);
    if (elMobileGrand) elMobileGrand.textContent = formatINR(grandTotal);
}

function syncCartInput() {
    const hiddenInput = document.getElementById('cartData');
    if (hiddenInput) {
        const payload = Object.values(cartState).map(i => ({
            id: i.id,
            quantity: i.quantity
        }));
        hiddenInput.value = JSON.stringify(payload);
    }
}

// Category & Search Filtering
function filterMenu() {
    const searchVal = (document.getElementById('menuSearchInput')?.value || '').toLowerCase().trim();
    const activeCategoryBtn = document.querySelector('.cat-filter-btn.active');
    const selectedCategory = activeCategoryBtn ? activeCategoryBtn.getAttribute('data-category') : 'all';
    const vegOnly = document.getElementById('dietFilterVeg')?.classList.contains('active') || false;

    const cards = document.querySelectorAll('.food-item-col');
    let visibleCount = 0;

    cards.forEach(card => {
        const itemCategory = card.getAttribute('data-category') || '';
        const itemName = (card.getAttribute('data-name') || '').toLowerCase();
        const itemDesc = (card.getAttribute('data-desc') || '').toLowerCase();
        const isVeg = card.getAttribute('data-veg') === 'true';

        const matchesCat = (selectedCategory === 'all' || itemCategory === selectedCategory);
        const matchesSearch = (!searchVal || itemName.includes(searchVal) || itemDesc.includes(searchVal));
        const matchesVeg = (!vegOnly || isVeg);

        if (matchesCat && matchesSearch && matchesVeg) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const noResultsEl = document.getElementById('noMenuResults');
    if (noResultsEl) {
        noResultsEl.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

// Category pill button click handler
function setCategory(category, buttonEl) {
    document.querySelectorAll('.cat-filter-btn').forEach(btn => btn.classList.remove('active'));
    if (buttonEl) buttonEl.classList.add('active');
    filterMenu();
}

// Veg-only toggle
function toggleVegOnly(buttonEl) {
    if (buttonEl) {
        buttonEl.classList.toggle('active');
    }
    filterMenu();
}

// Toast notification helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toastWrapper');
    if (!container) return;

    const toastId = 'toast_' + Date.now();
    const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'warning' ? 'bg-warning text-dark' : 'bg-dark text-white');

    const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    if (window.bootstrap && bootstrap.Toast) {
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }
}

// Checkout form submission handler
document.addEventListener('DOMContentLoaded', () => {
    initCart();

    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', function (e) {
            const items = Object.values(cartState);
            if (items.length === 0) {
                e.preventDefault();
                showToast('Please add at least one food item before placing an order!', 'warning');
                return;
            }

            syncCartInput();

            const submitBtn = document.getElementById('placeOrderButton');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Placing Order...';
            }
        });
    }

    // Attach search event
    const searchInput = document.getElementById('menuSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterMenu);
    }
});

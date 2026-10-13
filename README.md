# 🍽️ Smart Restaurant Food Ordering & Kitchen Dashboard
**Django Full-Stack Capstone Project — Production & Render Deployed**

A full-stack restaurant ordering portal and kitchen display system built with Django, Bootstrap 5, and JavaScript. Customers can explore gourmet dishes across categories, manage an interactive cart with live subtotal/tax calculations, submit table orders, and monitor real-time preparation progress with a 4-step live stepper. Kitchen staff can manage order preparation pipelines through a Kitchen Display System (KDS).

---

## 🌟 Key Features

### 👤 Customer Experience & Ordering Portal
- **Interactive Food Menu**: Responsive Bootstrap 5 food cards featuring high-resolution photography, dietary indicators (🟢 Pure Veg / 🔴 Non-Veg), descriptions, and pricing in INR (₹).
- **Category Filtering**: Fast dynamic filtering for **Appetizers**, **Main Course**, **Desserts**, and **Beverages**.
- **Instant Search & Pure Veg Filter**: Real-time dish search and a one-click Pure-Veg toggle.
- **Dynamic Shopping Cart**:
  - Item counter badge in navbar and mobile sticky bar.
  - Increment, decrement, and item removal controls.
  - Real-time Subtotal, 5% Restaurant GST Tax, and Grand Total computation.
  - Browser `localStorage` persistence across page reloads.
- **Robust Checkout Workflow**:
  - Full Name, 10-digit mobile number, and Table Number/Takeaway input.
  - Django ModelForm server-side validation.
  - CSRF-protected POST checkout.
  - Server-side price recalculation, availability verification, and session cart clearing.
- **Live Order Tracking**:
  - Real-time 4-step progress tracker: **Received ➔ Preparing ➔ Ready ➔ Completed**.
  - Animated pulsing indicator on the active preparation stage.
  - Live auto-refresh polling (every 8s) via JSON status API.
  - Search any order by numeric Order ID.

### 👨‍🍳 Kitchen Display System (KDS)
- **Live Operations Dashboard**: Protected staff dashboard for kitchen chefs.
- **Real-Time Digital Clock**: Monospace live clock for kitchen timing.
- **Order Pipeline Columns**: Instant visibility into Received, Preparing, Ready, and Completed orders.
- **Urgency Alerts**: Highlights tickets waiting longer than 20 minutes with a blinking `⚠️ URGENT` badge.
- **1-Click Status Progression**: Rapid one-tap advancement buttons (`Start Preparing 🍳` ➔ `Mark Ready 🔔` ➔ `Complete Order ✅`).
- **Auto-Refresh**: Live 10-second countdown with automatic background data sync.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons |
| **Backend** | Python 3.11+, Django 6.x |
| **Database** | SQLite (`db.sqlite3`) with Django ORM |
| **Static Assets** | WhiteNoise (`CompressedStaticFilesStorage`) |
| **WSGI Server** | Gunicorn |
| **Deployment** | Render (Web Service / Blueprint `render.yaml`) |

---

## 📁 Project Structure

```
Restaurant-Food-Ordering-Kitchen-Dashboard/
├── manage.py
├── requirements.txt
├── render.yaml
├── create_superuser.py
├── db.sqlite3
├── README.md
├── restaurant_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── restaurant_app/
    ├── migrations/
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── templates/
    │   └── restaurant_app/
    │       ├── home.html
    │       ├── order_success.html
    │       ├── track_order.html
    │       └── kitchen_dashboard.html
    └── static/
        ├── css/
        │   └── style.css
        ├── js/
        │   └── cart.js
        └── images/
            ├── spring_rolls.jpg
            ├── paneer.jpg
            ├── burger.jpg
            ├── pizza.jpg
            ├── biryani.jpg
            ├── chocolate_brownie.jpg
            ├── masala_chai.jpg
            └── lime_soda.jpg
```

---

## 🚀 Running Locally

1. **Clone or navigate to the repository**:
   ```bash
   cd "Restaurant Food Ordering & Kitchen Dashboard"
   ```

2. **Activate your Python environment**:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser and seed initial menu data**:
   ```bash
   python create_superuser.py
   ```
   *Default admin credentials: Username `admin` / Password `admin123` (or `madamsruthi` / `admin123`).*

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Open in browser**:
   - Customer Portal: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Order Tracking: [http://127.0.0.1:8000/track/](http://127.0.0.1:8000/track/)
   - Kitchen Dashboard: [http://127.0.0.1:8000/kitchen/](http://127.0.0.1:8000/kitchen/)
   - Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ☁️ Render Deployment Instructions

The application is fully pre-configured for deployment to **Render** using `render.yaml`.

1. **Push all code to your GitHub repository**:
   ```bash
   git add .
   git commit -m "Prepare Django project for Render"
   git push origin main
   ```

2. **Sign in to Render**:
   - Navigate to [dashboard.render.com](https://dashboard.render.com/).
   - Click **New +** ➔ **Blueprint** (or **Web Service**).
   - Connect your GitHub repository: `MADAM-SRUTHI/Smart-Restaurant-Food-Ordering-Kitchen-Dashboard`.

3. **Confirm Build & Start Commands**:
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py
     ```
   - **Start Command**:
     ```bash
     python manage.py migrate && python create_superuser.py && gunicorn restaurant_project.wsgi:application
     ```

4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.0`
   - `RENDER`: `True`
   - `SECRET_KEY`: `your-secure-production-secret-key`
   - `DJANGO_SUPERUSER_USERNAME`: `admin`
   - `DJANGO_SUPERUSER_PASSWORD`: `admin123`

5. **Verify the Live Deployment**:
   - Open your deployed URL: `https://<service-name>.onrender.com`.
   - Test placing an order, tracking order status, and updating tickets in the kitchen dashboard.

---

## 🔒 Security & Data Integrity
- Django CSRF token enforcement on all POST requests.
- Strict server-side recalculation of order totals and item availability.
- Quantity bounds validation (1 to 50 items).
- Protected staff authorization (`@staff_member_required`) for the kitchen dashboard.
- Safe static asset serving with WhiteNoise.

---

## 👩‍💻 Author
**Sruthi**  
*Capstone Project — Smart Restaurant Food Ordering & Kitchen Dashboard*

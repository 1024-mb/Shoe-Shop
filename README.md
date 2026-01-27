# Shoe Shop – Full-Stack E-Commerce Website (Django)

⚠️ **20-second demo:** https://youtu.be/D_WVxfMUiTU  

Shoe Shop is a fully functional e-commerce shoe store built with Django, featuring secure authentication, real-world payment processing, delivery integration, and end-to-end order management.

This project goes beyond a basic CRUD application and integrates Stripe, Lalamove, and Google Maps to simulate a production-grade online store.

---

## Table of Contents

- Key Features  
- Project Structure  
- Technologies Used  
- Payment and Delivery Flow  
- Setup Instructions  
- Environment Variables  
- Notes  
- Why This Project Matters  

---

## Key Features

- User registration, login, logout, and profile management  
- Email verification and authentication flow  
- Product browsing with size and color selection  
- Intelligent stock validation with real-time error handling  
- Shopping cart with dynamic updates  
- Secure checkout using Stripe Embedded Checkout  
- Webhook handling for payment confirmation  
- Delivery booking and tracking via Lalamove API  
- Order creation, cancellation, update, and status tracking  
- User reviews for purchased products  

---

## Project Structure

```text
├── base/
│   ├── Authentication (login, logout, registration)
│   ├── Email verification
│   └── Stripe webhook handling
│
├── cart/
│   ├── Cart management (GET, POST, clear)
│   └── Checkout flow
│
├── product/
│   ├── Product data retrieval
│   ├── Stock and variant validation
│   └── Add-to-cart logic
│
├── templates/
│   └── HTML templates for all pages
│
├── media/
│   └── Product images stored by product ID
│
└── db.sqlite3
```

---

## Technologies Used

### Backend
- Python (Django)
- SQLite3 (development database)
- Stripe API (payments and webhooks)
- Lalamove API (delivery fulfillment and tracking)
- Gmail API (email verification and notifications)

### Frontend
- HTML
- CSS
- JavaScript

### External Services
- Google Maps API (address autocomplete and validation)

---

## Payment and Delivery Flow

1. User adds items to the cart and proceeds to checkout  
2. Stripe Embedded Checkout validates:
   - Singapore delivery address  
   - Phone number  
3. Successful payment triggers a Stripe webhook  
4. Order is created server-side  
5. Delivery request is sent to the Lalamove API  
6. User can track, update, or cancel orders  

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher  
- pip  
- Virtual environment (recommended)  

### Local Setup

```bash
git clone https://github.com/yourusername/oe-shop.git
cd oe-shop
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Application runs at:
```
http://127.0.0.1:8000/
```

---

## Environment Variables

```env
DEBUG=True
SECRET_KEY=

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

LALAMOVE_API_KEY=

GOOGLE_MAPS_API_KEY=

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## Notes

- SQLite is used for development; PostgreSQL is recommended for production  
- Stripe is configured in test mode  
- Stripe webhooks require exposure via tools such as ngrok  
- Delivery functionality assumes valid Singapore addresses  

---

## Why This Project Matters

This project demonstrates:
- Integration with real-world payment and logistics APIs  
- Secure and scalable backend design using Django  
- Full e-commerce order lifecycle management  
- Practical full-stack engineering beyond coursework  

# SHOE SHOP WEBSITE

⚠️ Please watch my Demo (2-min): https://youtu.be/D_WVxfMUiTU ⚠️


## Introduction
This repository contains a fully-functional Django and HTML Shoe Shop website, complete with User Authentication, User Registration, Verification, Cart, Checkout, Review and Payment methods (embedded with Stripe). This app uses LalaMove to deliver goods and products. It is able to cancel, update, and view the status of orders.

## Directory Guide
**base:** handles user login, logout, profile updates, registration and email confirmation as well as stripe webhook event handling.

**cart:** handles the cart page - GET to get the contents of the cart, POST to update the contents, clearing the cart.

**cart:** handles the checkout page - implemented Stripe embedded checkout that allows the user to enter a Singapore address and a valid phone number with full validation.

**media:** contains product images for the product pages and home page, each stored according to its product id and sequence number.

**product:** responsible for the product page: gets product data from the server, select products based of size and color, intelligently processes stock data to provide users with error messages if the stock is below a certain level, and finally, allows authenticated users to add products to their carts.

**templates:** contains the HTML files used to render each of these pages

## Languages, Frameworks and Technologies
**Python** - uses the django framework to provide backend support, with databases and user authentication included. Used to store session data about orders and retrieve product data from databases as well as communicate with APIs from LalaMove and Gmail.

**JavaScript** - provides the user with interactive webpages with buttons that provide active feedback to the user.

**HTML & CSS** - used for front-end web layout and styling

**SQLite3** - lightweight database program used in this project

***
**Lalamove API -** used by website to fulfil orders.

**Stripe -** used to ensure user payment.

**Google Maps API -** used to allow delivery address lookup


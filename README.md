# 📦 Auction Furniture API

A backend REST API for managing furniture auctions, built with Flask, SQLAlchemy, and PostgreSQL.
The system supports users, furniture items, auction listings, bids, and notification.

The API is designed for educational/demo purposes and is fully testable via Postman.


## Requirements
- Python 3.10+ (earlier 3.x will probably work too)
- PostgreSQL 13+ (or compatible)
- pip for installing Python packages
  
Python packages used (install via pip):

- Flask
- SQLAlchemy
- psycopg2-binary
- python-dotenv
  
```bash
pip install Flask SQLAlchemy psycopg2-binary python-dotenv
```
___
## Configuration: .env
Configuration is read from environment variables using python-dotenv.

Example file: `.env`
```bash
# Copy this file to .env and fill in your local values

DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_DATABASE=my_app_db
```



## ✨ Features

- User registration, login (session-based), and authentication
- CRUD operations for furniture items
- Create & manage auctions
- Place bids on auctions
- Maintain a personal watchlist for auctions
- PostgreSQL relational database
- Ready-to-run with .env configuration
- Includes Postman collection


# 1. Project Overview

Auction Furniture API allows users to browse furniture, participate in auctions, and place bids in real time.
It is built for learning backend architecture, REST design, and database interaction.

# 2. Technical Architecture
## 🏛️ Architecture Summary

- Frontend: Any client (Postman, React, mobile app — not included in repo)

- Backend: Flask REST API

- Database: PostgreSQL

- ORM: SQLAlchemy

- Authentication: Flask signed session cookies

- External APIs: None

## 🔧 Why These Choices?

- Flask — lightweight, easy to understand for educational projects

- PostgreSQL — reliable SQL database for relational data

- SQLAlchemy — clean mapping between tables and Python logic

# 3. Installation & Running the Project
## 🔹 Requirements

- Python 3.10+

- PostgreSQL 13+

- pip (Python packages)

## 🔹 Install Python dependencies
```php
pip install Flask SQLAlchemy psycopg2-binary python-dotenv
```
or
```css
pip install -r requirements.txt
```

# 4. Configuration (.env)

Configuration is loaded using python-dotenv.

## Example .env

```ini
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_DATABASE=auction_furniture
SECRET_KEY=supersecretkey
```
## Setup
```bash
cp .env .env
```
Then edit .env with your own values.

main.py loads all environment variables automatically.

# 5. Database Setup

Your project includes create-database.sql.

## Create database
```psql
CREATE DATABASE auction_furniture;
```
## Import schema
```psql
psql -h localhost -U postgres -d auction_furniture -f create-database.sql
```
## Tables included

- users
- furniture
- auctions
- bids
- notification
- payment

(Optional) Add seed data for testing.

# 6. Running the Application
## (Recommended) Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

## Start backend
```bash
python main.py
```

API will run at:

👉 http://localhost:5000

# 7. Authentication & Sessions

- The system uses Flask session cookies:

- Logging in with POST /login sets a cookie

- All protected routes require that cookie

- Postman automatically stores and reuses cookies

Protected routes include:

- Creating furniture

- Creating auctions

- Placing bids

- Managing watchlists

- Admin-style operations

# 8. REST API Routes
## Users
### Method	Route	Description
POST	/users	Register a user
GET	/users	List all users (auth required)
Authentication
Method	Route	Description
POST	/login	Log in
GET	/login	Get currently logged-in user
DELETE	/login	Log out
Furniture
Method	Route	Description
GET	/furniture	List all furniture
GET	/furniture/<id>	Get furniture by ID
POST	/furniture	Create furniture (auth required)
PUT	/furniture/<id>	Update furniture
DELETE	/furniture/<id>	Delete furniture
Auctions
Method	Route	Description
GET	/auctions	List auctions
GET	/auctions/<id>	Get auction
POST	/auctions	Create auction (auth required)
PUT	/auctions/<id>	Update auction
DELETE	/auctions/<id>	Delete an auction
Bids
Method	Route	Description
GET	/auctions/<id>/bids	List bids for auction
POST	/bids	Place a bid (auth required)
Watchlist
Method	Route	Description
GET	/watchlist	Get user watchlist
POST	/watchlist	Add auction to watchlist
DELETE	/watchlist	Remove from watchlist
# 9. Testing
## Run tests
```bash
pytest
```
Types of tests included

❗ (If you want, I can generate these for you)
Common test types:

Unit tests (models + auth logic)

Integration tests (routes)

E2E tests via Postman

# 10. Build & Deployment
Build

No build step (Python project).

Deployment suggestions

Docker container

Railway / Render / Fly.io

Heroku (if using free tier alternatives)

GitHub Actions CI/CD

I can generate a full Dockerfile + docker-compose if you want.

# 11. Known Bugs / Limitations

No password hashing (can be added on request)

No real-time auction updates (WebSockets not implemented)

Basic session auth (JWT optional)

No admin panel

Minimal error handling in some routes

# 12. Demo Instructions
Test User

Email: test@example.com
Password: 123456

Suggested demo flow

1️⃣ Register or log in
2️⃣ List furniture
3️⃣ Create a new furniture item
4️⃣ Create an auction for an item
5️⃣ Place multiple bids
6️⃣ Show watchlist
7️⃣ Show error handling (insufficient bid, invalid auction, etc.)

# 13. Contact & Team

Developer: You

GitHub repo link

Project board

Documentation folder


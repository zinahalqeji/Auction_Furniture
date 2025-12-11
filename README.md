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

## Steps
1.Copy the example file:
```bash
cp .env.example .env
```
2.Edit `.env` and set:

- `DB_HOST` – host where PostgreSQL is running (often localhost or a container name)
- `DB_PORT` – PostgreSQL port (default 5432)
- `DB_USER` – PostgreSQL username
- `DB_PASSWORD` – PostgreSQL password
- `DB_DATABASE` – database name for this app, e.g. flasky_shop
  
3.`main.py` loads the .env on startup:
```bash
from dotenv import load_dotenv
load_dotenv()
```
The values are used to construct the SQLAlchemy URL:
```bash
url = URL.create(
    drivername="postgresql+psycopg2",
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)
```
___
## Database Setup
The project expects a PostgreSQL database with the schema defined in create-database.sql.
```bash
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    f_name VARCHAR,
    l_name VARCHAR,
    phone VARCHAR,
    email VARCHAR UNIQUE,
    password VARCHAR,
    role user_role NOT NULL,
    profile_picture TEXT
);
CREATE TABLE furniture_item (
    id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_name VARCHAR,
    description TEXT,
    category VARCHAR,
    material VARCHAR,
    dimensions VARCHAR,
    images TEXT,
    condition furniture_condition
);
CREATE TABLE auction (
    id SERIAL PRIMARY KEY,
    item_id INT NOT NULL UNIQUE REFERENCES furniture_item(id) ON DELETE CASCADE,
    seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    start_price DECIMAL,
    reserve_price DECIMAL,
    status auction_status
);
CREATE TABLE bid (
    id SERIAL PRIMARY KEY,
    auction_id INT NOT NULL REFERENCES auction(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL,
    bid_time TIMESTAMP
);
CREATE TABLE payment (
    id SERIAL PRIMARY KEY,
    auction_id INT NOT NULL REFERENCES auction(id) ON DELETE CASCADE,
    buyer_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL,
    commission_rate FLOAT,
    commission_amount DECIMAL,
    payment_date TIMESTAMP,
    net_amount DECIMAL,
    method payment_method,
    status payment_status,
    invoice_number VARCHAR
);
CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type,
    message TEXT,
    status notification_status,
    created_at TIMESTAMP
);
```
## Steps
1.Create the database in PostgreSQL (name must match `DB_DATABASE` in `.env`):
```bash
CREATE DATABASE auction_furniture;
```
Run the schema script:
```bash
psql -h localhost -U your_db_user -d auction_furniture -f create-database.sql
```
3.(Optional) Insert some initial data (e.g. items and auctions rows) using SQL or any DB tool.

Add default values in the DB
___

## Running the Application
From the project root:

1. (Optional but recommended) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate      # on macOS/Linux
# venv\Scripts\activate       # on Windows
```
2. Install dependencies (see above):
```bash
pip install -r requirements.txt
# or
pip install Flask SQLAlchemy psycopg2-binary python-dotenv
```
3. Make sure `.env` is configured and the database is created.

4. Run the app:
```bash
python main.py
```
By default Flask will run on:
```bash
http://localhost:5000
```
___

## Authentication & Sessions
- Authentication is session-based using Flask’s signed cookies.
- Logging in via POST /login will set a session cookie in the client.
- Routes decorated with @login_required will only work if that cookie is sent.
In Postman:

- When you call POST /login, Postman will automatically store the session cookie.
- Subsequent requests to protected routes (within the same collection/environment and to the same host) will automatically include the cookie.
  
 Protected routes (require login):

- GET /users
- POST /users
- GET /users/<user_id>
- PUT / users/<user_id>
- DELETE / users/<user_id>
- GET /auction
- POST /auction
- GET /auction/<auction_id>
- GET/ auction/ongoing
- DELETE /auction/<auction_id>
- GET /items
- POST /items
- GET /items/<items_id>
- PUT / items/<items_id>
- DELETE / items/<items_id>
- GET /payment
- POST /payment
- GET /payment/<payment_id>
- PUT / payments/<payment_id>
- DELETE / payment/<payment_id>
- GET /bids
- POST /bid
- GET /bids/<bid_id>
- PUT / bids/<bid_id>
- DELETE / bids/<bid_id>
___

## REST API
Base URL (local):
```bash
http://localhost:5000
```
### Users
`POST /users`
Create a new user.

- Auth: Public
- Body (JSON):
```bash
 {
        "email": "ava.patel@example.com",
        "f_name": "Ava",
        "l_name": "Patel",
        "password": "ava123",
        "phone": "555-0740",
        "profile_picture": "ava.jpg",
        "role": "buyer"
    }
```
- Responses:

- `201 Created `– user created successfully
- `400 Bad Request` – missing required fields
- `409 Conflict` – email already registered

`GET /users`
- Get all users.
- Auth: Requires login

Responses:

- 200 OK – list of users:
```bash
[
    {
        "email": "ava.patel@example.com",
        "f_name": "Ava",
        "id": 8,
        "l_name": "Patel",
        "password": "ava123",
        "phone": "555-0740",
        "profile_picture": "ava.jpg",
        "role": "buyer"
    }
]
```
- `401 Unauthorized `– if not logged in
___
### Auth
`POST /login`
Log in with email and password.

- Auth: Public
- Body (JSON):
```bash
{
  "email": "olle.wilson@example.com",
  "password": "olle123"
}
```
- Responses:

`200 OK `– login successful, session cookie set
```bash
{
  "message": "Login successful.",
  "user": {
    "id": 5,
    "name": "Olle",
    "email": "olle.wilson@example.com"
  }
}
```
- `400 Bad Request` – missing email or password
- `401 Unauthorized` – invalid credentials
- 
Passwords are stored in plaintext in this demo. This should be changed to proper password hashing in any real-world use.

`### GET /login`
Get the currently logged-in user (from session).

- Auth: Requires active session

- Responses:

`200 OK `– user info
`401 Unauthorized `– no user logged in or user not found (session is cleared)

`### DELETE /login`
Log out (clear session).

- Auth: Session-based

- Response:

`200 OK `– session cleared

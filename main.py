import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

# ----------------------------
# Environment & DB setup
# ----------------------------
load_dotenv()

# Ensure env values exist
required_env = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_DATABASE"]
for key in required_env:
    if not os.getenv(key):
        raise RuntimeError(f"Missing env var: {key}")

url = URL.create(
    drivername="postgresql+psycopg2",
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

engine = create_engine(url, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-this-in-production"

# ----------------------------
# Helper functions
# ----------------------------
def execute(query, params=None, fetch=None):
    with Session() as session:
        result = session.execute(text(query), params or {})
        session.commit()

        if fetch == "one":
            row = result.mappings().fetchone()
            return row
        if fetch == "all":
            rows = result.mappings().fetchall()
            return rows
        return None

def to_dict(row):
    return dict(row)  # now safe

# ----------------------------
# USERS CRUD
# ----------------------------

@app.get("/users")
def get_users():
    rows = execute("SELECT * FROM users", fetch="all")
    return jsonify([to_dict(row) for row in rows])

@app.get("/users/<int:user_id>")
def get_user(user_id):
    row = execute("SELECT * FROM users WHERE id=:id", {"id": user_id}, fetch="one")
    if not row:
        return {"message": "User not found"}, 404
    return to_dict(row)

@app.post('/users')
def create_user():
    data = request.get_json() or {}
    f_name = data.get("f_name")
    l_name = data.get("l_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    role = data.get("role")

    if not email or not password:
        return jsonify({"message": "Please provide email and password."}), 400

    with Session() as db:
        # check e-post
        existing = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing:
            return jsonify({"message": "Email already registered."}), 409

        # create user
        db.execute(
            text("""
                INSERT INTO users (f_name, l_name, email, password, phone, role)
                VALUES (:f_name, :l_name, :email, :password, :phone, :role)
            """),
            {"f_name": f_name, "l_name":l_name, "email": email, "password": password, "phone":phone, "role":role}
        )
        db.commit()

        # get new user
        new_user = db.execute(
            text("SELECT id, f_name,l_name, email, phone, role, password FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

    return jsonify({
        "message": "User created successfully.",
        "users": {
            "id": new_user.id,
            "f_name": new_user.f_name,
            "l_name": new_user.l_name,
            "email": new_user.email,
            "phone": new_user.phone,
            "password": new_user.password,
            "role": new_user.role
        }
    }), 201

@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    execute("DELETE FROM users WHERE id=:id", {"id": user_id})
    return {"message": "User deleted"}

@app.put("/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json() or {}

    # Fetch existing user
    existing_user = execute(
        "SELECT * FROM users WHERE id=:id",
        {"id": user_id},
        fetch="one"
    )

    if not existing_user:
        return jsonify({"message": "User not found"}), 404

    # Allowed fields to update
    fields = ["f_name", "l_name", "email", "phone", "password", "role"]

    # Prepare SQL SET part dynamically
    updates = []
    params = {"id": user_id}

    for field in fields:
        if field in data:
            updates.append(f"{field} = :{field}")
            params[field] = data[field]

    if not updates:
        return jsonify({"message": "No valid fields provided."}), 400

    update_query = f"""
        UPDATE users
        SET {', '.join(updates)}
        WHERE id = :id
    """

    # Execute update
    execute(update_query, params)

    # Fetch updated user
    updated_user = execute(
        "SELECT * FROM users WHERE id=:id",
        {"id": user_id},
        fetch="one"
    )

    return jsonify({
        "message": "User updated successfully.",
        "user": to_dict(updated_user)
    })


# ----------------------------
# Auction CRUD
# ----------------------------

@app.get("/auction/<int:auction_id>")
def get_auction(auction_id):
    row = execute("SELECT * FROM auction WHERE id=:id", {"id": auction_id}, fetch="one")
    if not row:
        return {"message": "auction not found"}, 404
    return to_dict(row)

@app.get("/auction")
def get_auctions():
    rows = execute("SELECT * FROM auction", fetch="all")
    return jsonify([to_dict(row) for row in rows])

@app.delete("/auction/<int:auction_id>")
def delete_auction(auction_id):
    execute("DELETE FROM auction WHERE id=:id", {"id": auction_id})
    return {"message": "auction deleted"}


@app.post("/auctions")
def create_auction():
    data = request.get_json() or {}
    required = ["item_id", "start_date", "end_date", "start_price", "reserve_price", "seller_id"]
    if not all(k in data for k in required):
        return {"error": f"Missing fields: {', '.join(required)}"}, 400

    data["status"] = "ongoing"
    execute("""
        INSERT INTO auction (item_id, seller_id, start_date, end_date, start_price, reserve_price, status)
        VALUES (:item_id, :seller_id, :start_date, :end_date, :start_price, :reserve_price, :status)
    """, data)
    new_auction = execute("SELECT * FROM auction ORDER BY id DESC LIMIT 1", fetch="one")
    return jsonify({
        "message": "Auction created successfully.",
        "auction": to_dict(new_auction)
    }), 201

@app.get("/auctions/ongoing")
def get_ongoing_auctions():
    auctions = execute("SELECT * FROM auction WHERE status='ongoing' ORDER BY end_date", fetch="all")
    return jsonify([to_dict(a) for a in auctions])

# ----------------------------
# Bid CRUD
# ----------------------------

@app.get("/bids")
def get_bids():
    rows = execute("SELECT * FROM bid", fetch="all")
    return jsonify([to_dict(row) for row in rows])

# ----------------------------
# Payment CRUD
# ----------------------------

@app.delete("/payment/<int:payment_id>")
def delete_payment(payment_id):
    execute(
        "DELETE FROM payment WHERE id = :id",
        params={"id": payment_id},
        fetch=None
    )
    return {"message": "Payment deleted"}

@app.get("/payment/<int:payment_id>")
def get_payment_by_id(payment_id):
    row = execute(
        "SELECT * FROM payment WHERE id = :id",
        params={"id": payment_id},
        fetch="one"
    )

    if row is None:
        return {"message": "Payment not found"}, 404

    return jsonify(to_dict(row))

@app.get("/payment")
def get_payment():
    rows = execute("SELECT * FROM payment", fetch="all")
    return jsonify([to_dict(row) for row in rows])


@app.put("/payments/<int:payment_id>")
def update_payment(payment_id):
    data = request.get_json() or {}
    allowed = ["status"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return {"error": "No valid fields to update"}, 400

    payment = execute("SELECT * FROM payment WHERE id=:id", {"id": payment_id}, fetch="one")
    if not payment:
        return {"error": "Payment not found"}, 404

    set_clause = ", ".join([f"{k} = :{k}" for k in updates])
    updates["id"] = payment_id
    execute(f"UPDATE payment SET {set_clause} WHERE id=:id", updates)
    updated = execute("SELECT * FROM payment WHERE id=:id", {"id": payment_id}, fetch="one")
    return to_dict(updated)




# ----------------------------
# Run App
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# ----------------------------
# Database connection
# ----------------------------
url = URL.create(
    drivername="postgresql+psycopg2",
    host="localhost",
    port=5432,
    username="postgres",
    password="123abc",
    database="auction_furniture"
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)

app = Flask(__name__)

# ----------------------------
# Helper functions
# ----------------------------
def to_dict(row):
    """Convert SQLAlchemy Row object to dictionary."""
    return dict(row._mapping)

def execute(query, params=None, fetch=None):
    with Session() as session:
        result = session.execute(text(query), params or {})
        session.commit()

        if fetch == "one":
            return result.fetchone()
        if fetch == "all":
            return result.fetchall()
        return None

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
        # Kolla om e-post redan finns
        existing = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing:
            return jsonify({"message": "Email already registered."}), 409

        # Skapa användare (plaintext password – byt till hashing senare!)
        db.execute(
            text("""
                INSERT INTO users (f_name, l_name, email, password, phone, role)
                VALUES (:f_name, :l_name, :email, :password, :phone, :role)
            """),
            {"f_name": f_name, "l_name":l_name, "email": email, "password": password, "phone":phone, "role":role}
        )
        db.commit()

        # Hämta nya användaren
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

@app.get("/auction")
def get_auction():
    rows = execute("SELECT * FROM auction", fetch="all")
    return jsonify([to_dict(row) for row in rows])



@app.get("/bids")
def get_bids():
    rows = execute("SELECT * FROM bid", fetch="all")
    return jsonify([to_dict(row) for row in rows])

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
# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)

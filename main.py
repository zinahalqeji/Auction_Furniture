from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# --------------------------
# Database Setup
# --------------------------

url = URL.create(
    drivername="postgresql+psycopg2",
    host="localhost",
    port=5432,
    username="postgres",
    password="2008",
    database="auction_furniture"
)

engine = create_engine(url, echo=False, future=True)
Session = sessionmaker(bind=engine, autoflush=False)

app = Flask(__name__)

# --------------------------
# Helper Functions
# --------------------------

def row_to_dict(row):
    """Convert SQLAlchemy Row object to dict."""
    return {
        "id": row.id,
        "f_name": row.f_name,
        "l_name": row.l_name,
        "phone": row.phone,
        "email": row.email
    }

# --------------------------
# Routes
# --------------------------

# GET all users
@app.get("/users")
def get_users():
    with Session() as session:
        result = session.execute(text("SELECT * FROM users"))
        rows = result.fetchall()

        users_list = [row_to_dict(row) for row in rows]

    return jsonify(users_list), 200


# GET user by ID
@app.get("/users/<int:user_id>")
def get_user(user_id):
    with Session() as session:
        row = session.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()

        if row is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify(row_to_dict(row)), 200


# POST create new user
@app.post("/users")
def create_user():
    data = request.get_json()

    with Session() as session:
        row = session.execute(
            text("""
                INSERT INTO users (f_name, l_name, phone, email)
                VALUES (:f_name, :l_name, :phone, :email)
                RETURNING id, f_name, l_name, phone, email
            """),
            data
        ).fetchone()

        session.commit()

    return jsonify({
        "message": "User created",
        "user": row_to_dict(row)
    }), 201


# PATCH update user
@app.patch("/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()

    with Session() as session:
        row = session.execute(
            text("""
                UPDATE users
                SET 
                    f_name = COALESCE(:f_name, f_name),
                    l_name = COALESCE(:l_name, l_name),
                    phone  = COALESCE(:phone, phone),
                    email  = COALESCE(:email, email)
                WHERE id = :id
                RETURNING id, f_name, l_name, phone, email
            """),
            {
                "id": user_id,
                "f_name": data.get("f_name"),
                "l_name": data.get("l_name"),
                "phone": data.get("phone"),
                "email": data.get("email")
            }
        ).fetchone()

        session.commit()

        if row is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "message": "User updated",
            "user": row_to_dict(row)
        }), 200


# DELETE user
@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    with Session() as session:
        row = session.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"),
            {"id": user_id}
        ).fetchone()

        session.commit()

        if row is None:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"message": "User deleted"}), 200


# --------------------------
# Run App
# --------------------------

if __name__ == "__main__":
    app.run(debug=True)

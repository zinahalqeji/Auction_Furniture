from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

# Database connection
url = URL.create(
    drivername="postgresql+psycopg2",
    host="localhost",
    port=5432,
    username="postgres",
    password="2008",
    database="auction_furniture"
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)

app = Flask(__name__)

# GET all users
@app.get('/users')
def get_users():
    with Session() as session:
        result = session.execute(text("SELECT * FROM users")).fetchall()
        users_list = [
            {
                "id": row.id,
                "f_name": row.f_name,
                "l_name": row.l_name,
                "phone": row.phone,
                "email": row.email
            } for row in result
        ]
    return jsonify(users_list), 200

# GET single user by ID
@app.get('/users/<int:user_id>')
def get_user(user_id: int):
    with Session() as session:
        row = session.execute(
            text("SELECT * FROM users WHERE id=:id"),
            {"id": user_id}
        ).fetchone()

        if not row:
            return jsonify({"message": "user not found"}), 404

        user = {
            "id": row.id,
            "f_name": row.f_name,
            "l_name": row.l_name,
            "phone": row.phone,
            "email": row.email
        }
        return jsonify(user), 200

# POST create new user
@app.post('/users')
def create_user():
    data = request.get_json()
    with Session() as session:
        session.execute(
            text("INSERT INTO users (f_name, l_name, phone, email) VALUES (:f_name, :l_name, :phone, :email)"),
            {
                "f_name": data["f_name"],
                "l_name": data["l_name"],
                "phone": data["phone"],
                "email": data["email"]
            }
        )
        session.commit()
    return jsonify({"message": "User created"}), 201

# PATCH update user
@app.patch('/users/<int:user_id>')
def update_user(user_id: int):
    data = request.get_json()
    with Session() as session:
        result = session.execute(
            text("UPDATE users SET f_name=:f_name, l_name=:l_name, phone=:phone, email=:email WHERE id=:id"),
            {
                "f_name": data.get("f_name"),
                "l_name": data.get("l_name"),
                "phone": data.get("phone"),
                "email": data.get("email"),
                "id": user_id
            }
        )
        session.commit()
        if result.rowcount == 0:
            return jsonify({"message": "user not found"}), 404
    return jsonify({"message": "User updated"}), 200

# DELETE user
@app.delete('/users/<int:user_id>')
def delete_user(user_id: int):
    with Session() as session:
        result = session.execute(
            text("DELETE FROM users WHERE id=:id"),
            {"id": user_id}
        )
        session.commit()
        if result.rowcount == 0:
            return jsonify({"message": "user not found"}), 404
    return jsonify({"message": "User deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)

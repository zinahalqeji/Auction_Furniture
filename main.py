from flask import Flask, jsonify, request
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

url = URL.create(
    drivername="postgresql+psycopg2",
    host="localhost",
    port=5432,
    username="postgres",
    password="2008",
    database="auction_furniture"
)

engine = create_engine(url)

app = Flask(__name__)
Session = sessionmaker(bind=engine)

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

@app.get('/users/<int:user_id>')
def get_user(user_id:int):
    with Session() as session:
        result = session.execute(text("SELECT * FROM users WHERE id=:id"),{"id":user_id}).fetchall()
        if not result:
            return jsonify({"message": "user not found"}), 404
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


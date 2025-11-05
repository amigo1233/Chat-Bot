from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("DB connected successfully")
        except Exception as e:
            print("DB connection failed:", e)
    app.run(debug=True)

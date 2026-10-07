from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'  # Explicitly specify the table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Add extend_existing=True to avoid issues when reloading
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<User {self.name}>'

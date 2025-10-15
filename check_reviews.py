from models import db, Review
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
db.init_app(app)

with app.app_context():
    bad_reviews = Review.query.filter(Review.rating.is_(None)).all()
    print(f'Bad reviews: {len(bad_reviews)}')
    for r in bad_reviews:
        print(f'ID {r.id}: rating={r.rating}')

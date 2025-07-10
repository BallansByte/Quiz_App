from app import create_app, db
from app.models import Question

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Sample questions
    q1 = Question(question_text="What is the capital of France?", option_a="Paris", option_b="Berlin", option_c="London", option_d="Rome", correct_answer="A")
    q2 = Question(question_text="What is 2 + 2?", option_a="3", option_b="4", option_c="5", option_d="6", correct_answer="B")

    db.session.add_all([q1, q2])
    db.session.commit()

    print("Database seeded successfully!")

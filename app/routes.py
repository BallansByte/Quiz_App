from flask import render_template, redirect, url_for, request, flash, session
from .forms import RegisterForm, LoginForm
from flask import Blueprint

main = Blueprint('main', __name__)

quiz_questions = [
    {
        'id': 1,
        'question': 'What is the capital of France?',
        'options': ['Paris', 'London', 'Berlin', 'Madrid'],
        'answer': 'Paris'
    },
    {
        'id': 2,
        'question': 'Which planet is known as the Red Planet?',
        'options': ['Earth', 'Mars', 'Jupiter', 'Venus'],
        'answer': 'Mars'
    },
    {
        'id': 3,
        'question': 'What is the largest ocean on Earth?',
        'options': ['Atlantic', 'Pacific', 'Indian', 'Arctic'],
        'answer': 'Pacific'
    }
]

@main.route('/')
def home():
    return render_template('home.html')

# In-memory user store (temporary, until we use DB)
users = {}

@main.route('/register', methods=['GET', 'POST'])
def register():
    from .models import User
    from . import db
    from .forms import RegisterForm  # Make sure this is imported too

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check for existing username or email
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please login or use a different one.', 'danger')
            return redirect(url_for('main.login'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)



@main.route('/login', methods=['GET', 'POST'])
def login():
    from .models import User
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session.permanent = True
            session['user'] = user.username
            session['user_id'] = user.id  # ✅ Store user_id for result saving
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
def dashboard():
    from .models import QuizResult, User

    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('main.login'))

    user = session['user']
    user_obj = User.query.filter_by(username=user).first()
    results = []

    if user_obj:
        results = QuizResult.query.filter_by(user_id=user_obj.id).order_by(QuizResult.timestamp.desc()).all()

    return render_template('dashboard.html', username=user, results=results)

@main.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/quiz', methods=['GET', 'POST'])
def quiz():
    from .models import Question, QuizResult
    from . import db

    if 'score' not in session:
        session['score'] = 0
        session['question_number'] = 0
        session['asked_questions'] = []

    if request.method == 'POST':
        selected_answer = request.form.get('answer')
        question_id = session.get('current_question_id')

        if question_id:
            question = Question.query.get(question_id)
            if selected_answer == question.correct_answer:
                session['score'] += 1
                flash("Correct!", "success")
            else:
                correct_option = getattr(question, f"option_{question.correct_answer.lower()}")
                flash(f"Wrong! The correct answer was: {question.correct_answer}. {correct_option}", "danger")

            session['question_number'] += 1
            session['asked_questions'].append(question.id)

        return redirect(url_for('main.quiz'))

    # GET Request: fetch a new question
    asked = session.get('asked_questions', [])
    question = Question.query.filter(~Question.id.in_(asked)).first()

    if not question:
        final_score = session.get('score', 0)
        total = session.get('question_number', 0)
        percentage = round((final_score / total) * 100, 2) if total > 0 else 0

        # ✅ Always define result_data first
        result_data = {
            'score': final_score,
            'total': total,
            'percentage': percentage
        }

        # ✅ Save to DB only if user is logged in
        if 'user_id' in session:
            result = QuizResult(
                user_id=session['user_id'],
                score=final_score,
                total_questions=total
            )
            db.session.add(result)
            db.session.commit()

        # clear quiz data (to keep user logged in)
        session.pop('score', None)
        session.pop('question_number', None)
        session.pop('asked_questions', None)
        session.pop('current_question_id', None)

        return render_template('result.html', **result_data)

    session['current_question_id'] = question.id
    return render_template('quiz.html', question=question)


@main.route('/api/questions', methods=['GET'])
def get_questions():
    from .models import Question
    from flask import jsonify

    questions = Question.query.all()
    result = []

    for q in questions:
        result.append({
            'id': q.id,
            'question_text': q.question_text,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d
            }
        })

    return jsonify({'questions': result})

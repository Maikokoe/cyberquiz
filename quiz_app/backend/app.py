from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from questions import QUIZ_QUESTIONS, get_questions_by_category, get_all_categories, get_question_by_id
from db import init_db, get_or_create_user, save_attempt, get_user_stats, get_user_history, get_leaderboard

backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

init_db()

@app.route('/')
def index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({"categories": get_all_categories()})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    limit = request.args.get('limit', 10, type=int)
    questions = get_questions_by_category(category, difficulty)
    import random
    random.shuffle(questions)
    questions = questions[:limit]
    safe_questions = [{"id": q["id"], "question": q["question"], "options": q["options"], "category": q["category"], "difficulty": q["difficulty"]} for q in questions]
    return jsonify({"questions": safe_questions})

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    q = get_question_by_id(question_id)
    if q:
        return jsonify(q)
    return jsonify({"error": "Question not found"}), 404

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    user_name = data.get('user_name', 'Guest')
    user_email = data.get('user_email', f'guest_{os.getenv("RANDOM", "0")}@quiz.local')
    category = data.get('category')
    answers = data.get('answers', [])
    user_id = get_or_create_user(user_name, user_email)
    correct = 0
    total = len(answers)
    detailed_results = []
    for answer in answers:
        q_id = answer.get('question_id')
        selected = answer.get('selected_option')
        question = get_question_by_id(q_id)
        if question:
            is_correct = selected == question['correct']
            if is_correct:
                correct += 1
            detailed_results.append({"question_id": q_id, "question": question['question'], "selected": question['options'][selected] if 0 <= selected < len(question['options']) else None, "correct_answer": question['options'][question['correct']], "is_correct": is_correct, "explanation": question['explanation']})
    time_taken = data.get('time_taken', 0)
    save_attempt(user_id, category, correct, total, time_taken)
    percentage = round(correct / total * 100, 1) if total > 0 else 0
    return jsonify({"score": correct, "total": total, "percentage": percentage, "user_id": user_id, "results": detailed_results})

@app.route('/api/user/<int:user_id>/stats', methods=['GET'])
def user_stats(user_id):
    stats = get_user_stats(user_id)
    if stats:
        return jsonify(stats)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/user/<int:user_id>/history', methods=['GET'])
def user_history(user_id):
    history = get_user_history(user_id)
    return jsonify({"history": history})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    limit = request.args.get('limit', 10, type=int)
    board = get_leaderboard(limit)
    return jsonify({"leaderboard": board})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

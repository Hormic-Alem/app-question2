import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap
from random import choice

app = Flask(__name__)
app.secret_key = 'mysecretkey'
Bootstrap(app)

# Archivo para guardar usuarios
USERS_FILE = 'users.txt'

# Base de datos de preguntas por área
questions_db = {
    'Derecho': [
        {'question': '¿Qué es el delito?', 'answer': 'Delito es aquello del dolo'},
        {'question': '¿Qué es derecho?', 'answer': 'sobre el derecho'},
        {'question': '¿Que es dolo?', 'answer': 'sobre el dolo es intención'}
    ],
    'Medicina': [
        {'question': 'Pregunta 1 sobre Medicina', 'answer': 'Respuesta 1 sobre Medicina'},
        {'question': 'Pregunta 2 sobre Medicina', 'answer': 'Respuesta 2 sobre Medicina'},
        {'question': 'Pregunta 3 sobre Medicina', 'answer': 'Respuesta 3 sobre Medicina'}
    ],
    'Psicología': [
        {'question': 'Pregunta 1 sobre Psicología', 'answer': 'Respuesta 1 sobre Psicología'},
        {'question': 'Pregunta 2 sobre Psicología', 'answer': 'Respuesta 2 sobre Psicología'},
        {'question': 'Pregunta 3 sobre Psicología', 'answer': 'Respuesta 3 sobre Psicología'}
    ]
}

# Funciones para manejo de usuarios
def load_users():
    """Carga los usuarios del archivo a un diccionario."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as file:
        users = {}
        for line in file:
            username, password = line.strip().split(':')
            users[username] = password
        return users

def save_user(username, password):
    """Guarda un nuevo usuario en el archivo."""
    with open(USERS_FILE, 'a') as file:
        file.write(f'{username}:{password}\n')

# Cargar usuarios al iniciar la app
users_db = load_users()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users_db and users_db[username] == password:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return "Usuario o contraseña incorrectos. <a href='/'>Intentar de nuevo</a>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username not in users_db:
            users_db[username] = password
            save_user(username, password)  # Guardar en el archivo
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Usuario ya registrado"
    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/area/<area>')
def area(area):
    if 'username' not in session:
        return redirect(url_for('index'))
    
    questions = questions_db.get(area, [])
    return render_template('area.html', area=area, questions=questions)

@app.route('/question_trainer/<area>/<path:question>', methods=['GET', 'POST'])
def question_trainer(area, question):
    if 'username' not in session:
        return redirect(url_for('index'))

    from urllib.parse import unquote
    question = unquote(question)

    question_data = next((item for item in questions_db.get(area, []) if item['question'] == question), None)

    if not question_data:
        return "Pregunta no encontrada."

    return render_template('question_trainer.html', area=area, question=question_data['question'], answer=question_data['answer'])

@app.route('/quick_trainer', methods=['GET', 'POST'])
def quick_trainer():
    if 'username' not in session:
        return redirect(url_for('index'))

    all_questions = [q for questions in questions_db.values() for q in questions]
    random_question = choice(all_questions)

    if request.method == 'POST':
        user_answer = request.form['user_answer']
        correct_answer = random_question['answer']

        if user_answer.strip().lower() == correct_answer.strip().lower():
            feedback = "¡Correcto! 🎉"
        else:
            feedback = f"Incorrecto. La respuesta correcta es: {correct_answer}"

        return render_template(
            'quick_trainer.html',
            question=random_question['question'],
            feedback=feedback
        )

    return render_template('quick_trainer.html', question=random_question['question'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


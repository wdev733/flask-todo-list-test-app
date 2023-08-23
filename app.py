from flask import Flask, redirect, url_for, render_template, request
from models import db, User, ToDO
from datetime import datetime

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00'
app.config['DEBUG'] = True

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db.init_app(app)

@app.route("/", methods=['POST', 'GET'])
def mainPage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username, password = password).first()
        if user:
            return redirect('/user/' + str(user.id) + '/tasks')
        return redirect('/')
    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user= User(username = username, password = password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/user/' + str(new_user.id) + '/tasks')
        except:
            return 'There was an issue creating your account'
    else:
        return render_template('signup.html')

@app.route('/user/<string:user_id>/tasks', methods=['POST', 'GET'])
def get_all_tasks(user_id):
    if request.method == 'POST':
        task_name = request.form['task_name']
        due_date = datetime.strptime(request.form['task_due_date'], '%Y-%m-%d')

        new_task = ToDO(task_name = task_name, due_date = due_date, completed = False, user_id = int(user_id))
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/user/' + str(user_id) + '/tasks')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = ToDO.query.filter_by(user_id = user_id).order_by(ToDO.date_created).all()
        user = User.query.filter_by(id = user_id).first()
        return render_template('task_list.html', tasks = tasks, user=user)


@app.route('/delete/<int:user_id>/<int:task_id>')
def delete(user_id, task_id):
    task = ToDO.query.filter_by(id = task_id, user_id = user_id).first()

    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/user/' + str(user_id) + '/tasks')
    except:
        return 'Unexepected error in deleting that task'


@app.route('/complete/<int:user_id>/<int:task_id>')
def complete(user_id, task_id):
    task = ToDO.query.filter_by(id = task_id, user_id = user_id).first()
    task.completed = True

    try:
        db.session.commit()
        return redirect('/user/' + str(user_id) + '/tasks')
    except:
        return 'Unexepected error in completing that task'


@app.route('/update/<int:user_id>/<int:task_id>', methods=['GET', 'POST'])
def update(user_id, task_id):
    task = ToDO.query.filter_by(id = task_id, user_id = user_id).first()

    if request.method == 'POST':
        task.task_name = request.form['task_name']
        task.due_date = datetime.strptime(request.form['task_due_date'], '%Y-%m-%d')

        try:
            db.session.commit()
            return redirect('/user/' + str(user_id) + '/tasks')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('task_update.html', task = task, user_id = user_id)

if __name__ == "__main__":
    app.run(port=3000)

from flask import Flask, render_template, request, redirect, jsonify, json
from flask.json import JSONEncoder
from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy
from webassets import Bundle

app = Flask(__name__)

assets = Environment(app)
scss = Bundle('tasks.scss', filters='pyscss', output='tasks.css')
assets.register('scss_tasks', scss)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flask_todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Task(db.Model, JSONEncoder):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    details = db.Column(db.String(512), nullable=True)
    is_done = db.Column(db.Boolean, nullable=False, default=False)

    def default(self, o):
        return json.JSONEncoder.default(self, o)


@app.route('/')
def show_homepage():
    return redirect('/tasks')


@app.route('/tasks')
def index_tasks():
    tasks = Task.query.all()
    return render_template('task_list.html', tasks=tasks)


@app.route('/tasks/<task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.title = request.form['title']
    task.details = request.form['details']
    db.session.commit()

    return redirect('/tasks')


@app.route('/tasks', methods=['POST'])
def add_task():
    form = request.form
    task = Task(title=form['title'], details=form['details'])
    db.session.add(task)
    db.session.commit()

    return redirect('/tasks')


@app.route('/api/tasks/<task_id>', methods=['POST'])
def edit_task_via_api(task_id):
    if not (task_id is None):
        task = Task.query.filter_by(id=task_id).first()
    else:
        task = Task()
    task.is_done = request.get_json()['is_done']
    db.session.commit()

    return jsonify(id=task.id, title=task.title, details=task.details, is_done=task.is_done)


@app.route('/tasks/<task_id>', methods=['GET'])
def show_edit_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    return render_template('edit_task.html', task=task)


@app.route('/tasks/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    db.session.delete(task)
    db.session.commit()

    return redirect('/tasks')


@app.route('/tasks/add', methods=['GET'])
def show_add_task():
    return render_template('edit_task.html', task=Task(id='', title='', details=''))


if __name__ == '__main__':
    app.run()

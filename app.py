from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, required=True, help='Title is required')
task_parser.add_argument('description', type=str, required=True, help='Description is required')

class TaskResource(Resource):
    def get(self, task_id):
        task = Task.query.get(task_id)
        if task:
            return {'id': task.id, 'title': task.title, 'description': task.description}
        else:
            return {'error': 'Task not found'}, 404

    def put(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task not found'}, 404

        args = task_parser.parse_args()
        task.title = args['title']
        task.description = args['description']
        db.session.commit()

        return {'id': task.id, 'title': task.title, 'description': task.description}

class TaskListResource(Resource):
    def get(self):
        tasks = Task.query.all()
        return [{'id': task.id, 'title': task.title, 'description': task.description} for task in tasks]

    def post(self):
        args = task_parser.parse_args()
        new_task = Task(title=args['title'], description=args['description'])
        db.session.add(new_task)
        db.session.commit()

        return {'id': new_task.id, 'title': new_task.title, 'description': new_task.description}, 201

api.add_resource(TaskListResource, '/tasks')
api.add_resource(TaskResource, '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)

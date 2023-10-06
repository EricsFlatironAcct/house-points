#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, make_response, session, jsonify
from flask_restful import Resource
from sqlalchemy.sql import func
# Local imports
from config import app, db, api
# Add your model imports
from models import Family, User, Task

# Views go here!

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

class FamilyList(Resource):
    def get(self):
        family_dict = [f.to_dict(only=("id","family_name", "family_username", "users.name", "tasks.id")) for f in Family.query.all()]
        
        return make_response(family_dict, 200)
    def post(self):
        data = request.get_json()
        duplicate_family = Family.query.filter_by(family_username=data["username"]).first()
        if duplicate_family:
            return make_response({"error":"username already exists"},400)
        new_family = Family(
            family_username = data["username"],
            family_name = data["family_name"]
        )
        new_family.password_hash = data["password"]
        db.session.add(new_family)
        db.session.commit()
        session['family_id']=new_family.id
        response = make_response(
            new_family.to_dict(only=("id", "family_name", "family_username", "users.name", "tasks.id")),
            201
        )
        return response

class UserList(Resource):
    def get(self):
        user_dict = [u.to_dict(only=("id","name", "head_of_household", "family_id", "tasks.id")) for u in User.query.all()]
        return make_response(user_dict, 200)
    def post(self):
        user_json = request.get_json()
        name = user_json.get('name')
        if (not name): return make_response({"error" : "Must include a name"}, 400)
        head_of_household = user_json.get('head_of_household') or False
        family_id = user_json.get('family_id')
        new_user = User(
            name=user_json.get("name"),
            family_id=family_id,
            head_of_household=head_of_household
        )
        db.session.add(new_user)
        db.session.commit()
        resp = make_response(
            new_user.to_dict(only=("id","name", "head_of_household", "family_id", "tasks.id")),
            201
        )
        return resp
class TaskList(Resource):
    def get(self):
        task_dict = [t.to_dict(only=("id","title", "location", "description", "points", "frequency", "completed_by_user_id", "family_id")) for t in Task.query.all()]
        return make_response(task_dict, 200)
    
class Login(Resource):

    def post(self):

        username = request.get_json()['username']
        family = Family.query.filter_by(family_username=username).first()
        if not family:
            return {'error': 'Invalid username or password'}, 401
        password = request.get_json()['password']

        if family.authenticate(password):
            session['family_id'] = family.id
            return family.to_dict(only=("id","family_name", "family_username", "users.name", "tasks.id")), 200

        return {'error': 'Invalid username or password'}, 401
    
class Logout(Resource):
    def delete(self):
        session['family_id'] = None
        return make_response({'message': '204: No Content'}, 204)

class UserByFamily(Resource):
    def get(self, id):
        user_dict = [u.to_dict(only=("id","name", "head_of_household", "family_id", "tasks.id")) for u in User.query.filter_by(family_id=id).all()]
        return user_dict

class TasksByFamily(Resource):
    def get(self, id):
        task_dict = [t.to_dict(only=("id","title", "location", "description", "points", "frequency", "completed_by_user_id", "family_id")) for t in Task.query.filter_by(family_id=id).order_by("completed_by_user_id").all()]
        return make_response(task_dict, 200)
    def post(self, id):
        task_json = request.get_json()
        title = task_json.get("name"),
        description = task_json.get("description"),
        location = task_json.get("location", "home")
        if (len(location)<1): location = "home"
        points = task_json.get("frequency")
        family_id = id
        if (len(title) <1 or len(description)<1):
            return make_response({"error: ": "title and description required"}, 400)
        new_task = Task(
            title=title[0],
            description = description[0],
            location = location,
            points = points,
            family_id = family_id
        )
        db.session.add(new_task)
        db.session.commit()
        new_task_dict = new_task.to_dict(only=("id","title", "location", "description", "points", "frequency", "family_id"))
        return (new_task_dict, 200)
    def patch(self, id):
        request_json = request.get_json()
        task = Task.query.filter_by(id=id).first()
        for attr in request_json:
            setattr(task, attr, request.get_json()[attr])
        db.session.add(task)
        db.session.commit()
        
        response_dict = task.to_dict(only=("id","title", "location", "description", "points", "frequency", "completed_by_user_id", "family_id"))

        return make_response(
            response_dict,
            200
        )
    def delete(self, id):
        task = Task.query.filter_by(id=id).first()
        db.session.delete(task)
        db.session.commit()
        return ({"message": "successfully deleted task"}, 200)


class CheckSession(Resource):
    def get(self):
        print(session.get('family_id'))
        family = Family.query.filter_by(id =session.get('family_id')).first()
        if family:
            return family.to_dict(only=("id", "family_name", "family_username"))
        else:
            return make_response({'message': '401: Not Authorized'}, 401)

class PointsByUser(Resource):
    def get(self, id):
        user_points = db.session.query(func.sum(Task.points)).filter_by(completed_by_user_id=1).first()[0]
        #db.session.query(db.func.sum(Task.points)).filter(Task.completed_by_user_id==1).first()
        user_points_dict = {"points": user_points}
        return make_response(user_points_dict, 200)
class PointsByFamily(Resource):
    def get(self, id):
        user_list= User.query.filter_by(family_id=id).all()
        user_scores = [{"user_id":user.id, "points": db.session.query(func.sum(Task.points)).filter_by(completed_by_user_id=user.id).first()[0] or 0} for user in user_list]
        return make_response({"score_list": user_scores}, 200)
    
api.add_resource(PointsByFamily, '/scoreboard/family/<int:id>', endpoint = 'scoreboard/family/<int:id>')
api.add_resource(PointsByUser, '/scoreboard/<int:id>', endpoint='scoreboard/<int:id>')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(TasksByFamily, '/tasks/family/<int:id>', endpoint='tasks/family/<int:id>')    
api.add_resource(UserByFamily, '/users/family/<int:id>', endpoint='user/family/<int:id>')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(TaskList, '/tasks', endpoint='tasks')
api.add_resource(UserList, '/users', endpoint='users')
api.add_resource(FamilyList, '/families', endpoint='families')
if __name__ == '__main__':
    app.run(port=5555, debug=True)


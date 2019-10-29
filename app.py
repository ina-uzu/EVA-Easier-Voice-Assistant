from flask import Flask
from flask import request
from flask_restful import Resource,reqparse, Api
from dao import userdao, shortcutdao

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Easier Voice Assistant'


@app.route('/user', methods=['GET'])
def get_all_user():
    return userdao.fina_all()


@app.route('/user', methods=['POST'])
def create_user():
    try:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str, help='name cannot be blank')
        args = parser.parse_args()
        return userdao.add(str(args['name']))
    except Exception as e :
        return {'error': str(e)}


@app.route('/shortcut', methods=['GET'])
def get_all_shortcuts():
    try:
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, type=int, help='user_id cannot be blank')
        args = parser.parse_args()
        return shortcutdao.find_by_user(args['user_id'])

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut', methods=['POST'])
def create_shortcut():
    print(request.args)
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']

            if 'keyword' in request.args and 'command' in request.args :
                return shortcutdao.add(user_id, request.args['keyword'], request.args['command'])
        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

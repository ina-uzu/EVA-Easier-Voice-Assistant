from flask import Flask
from flask import request
from flask_restful import Resource,reqparse, Api
from dao import userdao, shortcutdao

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Easier Voice Assistant'


@app.route('/user', methods=['POST'])
def create_user():
    try:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str, help='name cannot be blank')
        args = parser.parse_args()
        return userdao.add(str(args['name']))
    except Exception as e :
        return {'error': str(e)}


@app.route('/user', methods=['DELETE'])
def find_user_by_id(u):
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']
            return userdao.delete_by_id(user_id)
        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/user', methods=['GET'])
def find_all_users():
    return userdao.find_all()


@app.route('/user', methods=['GET'])
def find_user_by_id(u):
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']
            return userdao.find_by_id(user_id)

        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut', methods=['POST'])
def create_shortcut():
    print(request.args)
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']

            if 'keyword' in request.args and 'command' in request.args:
                return shortcutdao.add(user_id, request.args['keyword'], request.args['command'])

            else:
                print("keyword & command REQUIRED")
        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut/delete', methods=['DELETE'])
def delete_all_shortcuts():
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']
            return shortcutdao.delete_all(user_id)

        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut', methods=['DELETE'])
def delete_shortcut_by_keyword():
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']

            if 'keyword' in request.args:
                return shortcutdao.delete_by_keyword(user_id, request.args['keyword'])

            else:
                print("keyword REQUIRED")

        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut', methods=['DELETE'])
def find_all_shortcuts():
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']
            return shortcutdao.find_all(user_id)

        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/shortcut', methods=['DELETE'])
def find_shortcut_by_keyword():
    try:
        if 'user_id' in request.args:
            user_id = request.args['user_id']

            if 'keyword' in request.args:
                return shortcutdao.find_by_keyword(user_id, request.args['keyword'])

            else:
                print("keyword REQUIRED")

        else:
            print("user_id REQUIRED")

    except Exception as e:
        return {'error': str(e)}


@app.route('/stt', methods=['POST'])
def send_stt():
    try:
        if 'stt' in request.args:
            stt = request.args['stt']
            return stt
        else:
            print("stt REQUIRED")

    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

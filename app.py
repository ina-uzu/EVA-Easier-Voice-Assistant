from flask import Flask
from flask import request
from flask_restplus import Resource, Api, fields
from dao import userdao, shortcutdao

app = Flask(__name__)
api = Api(app, version='1.0', title='EVA API', description='Easier Voice Assistant')
ns = api.namespace('user', description='User CRD')
sc_ns = api.namespace('shortcut', description='Shortcut CRD')
stt_ns = api.namespace('stt', description='stt 전송')

user_model = api.model('Model', {
    'id': fields.Integer,
    'name': fields.String,
})

shortcut_model = api.model('Model', {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'keyword': fields.String,
    'command': fields.String
})


class User(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Shortcut(object):
    def __init__(self, id, user_id, keyword, command):
        self.id = id
        self.user_id = user_id
        self.keyword = keyword
        self.command = command


@ns.route('/', methods=['GET', 'POST'])
class UserManager(Resource):
    def get(self):
        try:
            return userdao.find_all()

        except Exception as e:
            return {'error': str(e)}

    @ns.param('name', '사용자 이름을 입력하세요')
    def post(self):
        try:
            if 'name' in request.args:
                name = request.args['name']
                return userdao.add(name)
            else:
                print("name REQUIRED")

        except Exception as e:
            return {'error': str(e)}


@ns.route('/<int:id>', methods=['GET', 'DELETE'])
class UserManager(Resource):
    def get(self, id):
        try:
            data = userdao.find_by_id(id)
            return data

        except Exception as e:
            return {'error': str(e)}

    def delete(self, id):
        try:
            return userdao.delete_by_id(id)

        except Exception as e:
            return {'error': str(e)}


@sc_ns.route('/', methods=['GET', 'DELETE'])
class ShortcutManager(Resource):
    def get(self):
        try:
            return shortcutdao.find_all()

        except Exception as e:
            return {'error': str(e)}

    def delete(self):
        try:
            return shortcutdao.delete_all()

        except Exception as e:
            return {'error': str(e)}


@sc_ns.route('/<int:user_id>', methods=['GET', 'POST', 'DELETE'])
class ShortcutMangerWithUser(Resource):
    @ns.param('keyword', '검색할 단축키를 입력하세요')
    def get(self, user_id):
        try:
            if 'keyword' in request.args:
                return shortcutdao.find_by_keyword(user_id, request.args['keyword'])

            else:
                return shortcutdao.find_by_user(user_id)

        except Exception as e:
            return {'error': str(e)}

    @ns.param('keyword', '단축키로 등록할 단어를 입력하세요')
    @ns.param('command', '단축키에 맵핑시킬 기능을 입력하세요')
    def post(self, user_id):
        try:
            if 'keyword' in request.args and 'command' in request.args:
                return shortcutdao.add(user_id, request.args['keyword'], request.args['command'])

            else:
                print("keyword & command REQUIRED")

        except Exception as e:
            return {'error': str(e)}

    @ns.param('keyword', '삭제찰 단축키를 입력하세요')
    def delete(self, user_id):
        try:
            if 'keyword' in request.args:
                return shortcutdao.delete_by_keyword(user_id, request.args['keyword'])

            else:
                return shortcutdao.delete_by_user(user_id)

        except Exception as e:
            return {'error': str(e)}


@stt_ns.route('/', methods=['POST'])
class DeviceManager(Resource):
    def post(self):
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

from flask import Flask
from flask_restful import Resource,reqparse, Api
from dao import userdao

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/user', methods=['GET'])
def getAllUser():
    return userdao.getAllUsers()

@app.route('/user', methods=['POST'])
def createUser():
    try:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str, help='name cannot be blank')
        args = parser.parse_args()
        return userdao.createUser(str(args['name']))
    except Exception as e :
        return {'error': str(e)}


class test(Resource):
    def post(self):
        return {'status': 'success'}
 
api.add_resource(test, '/test')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

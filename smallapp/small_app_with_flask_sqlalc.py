import json

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3308/testcases?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    steps = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # return {
        #     "id": self.id,
        #     "name": self.name,
        #     "description": self.description,
        #     "steps": self.steps,
        # }
class TestCaseServerORM(Resource):
    # 如果是get请求，认为是去查询所有case
    def get(self):
        app.logger.info(request.args)
        case_id = request.args.get("id")
        if case_id:
            case_data = TestCase.query.filter_by(id=case_id).first()
            testcases = [case_data.as_dict()]
        else:
            case_data = TestCase.query.all()
            testcases = [i.as_dict() for i in case_data]
            print(testcases)
        return {"data": testcases}

    # 如果是post请求，认为是去新增case
    def post(self):
        app.logger.info(request.args)
        app.logger.info(request.json)
        # 通过接口发送的数据进行TestCaseList类的实例化
        try:
            testcase = TestCase(**request.json)
            testcase.steps = json.dumps(request.json.get("steps"))
            app.logger.info(testcase)
            db.session.add(testcase)
            db.session.commit()
            db.session.close()
            return {
                "error": 0,
                "msg": "OK"
            }
        except:
            return {
                "error": 500,
                "msg": "server has an error!"
            }


# 注册到flask_restful api中去
api.add_resource(TestCaseServerORM, '/testcase_orm')

if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    #     result = db.session.query(TestCase).all()
    #     for item in result:
    #         print(item)
    app.run(debug=True, use_reloader=True, port=5000)

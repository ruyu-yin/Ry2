import json
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename, redirect
import os
from flask import Flask, request, flash, url_for, send_from_directory, render_template,redirect
# from flask import current_app as app
from flask_restful import Resource, Api,reqparse
from flask_sqlalchemy import SQLAlchemy
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import login_user, login_required, logout_user, UserMixin, login_manager,LoginManager
# import sqlalchemy_utils
import click




app = Flask(__name__)
app.env = 'development' #设置应用程序为开发环境
CORS(app, supports_credentials=True)
api = Api(app)
prefix = 'mysql+pymysql://root:123456@localhost:3308/'
db_name = 'userdata'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3308/testcases?charset=utf8'
app.config['SQLALCHEY_BINDS'] = {'secondary_db':prefix + db_name}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = secrets.token_hex(32)
# db_secondary = SQLAlchemy(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

class User(db.Model):
    __bind_key__ = 'secondary_db'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(255))
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值



class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=False)
    cyclename = db.Column(db.String(80),unique=False)
    executionresult = db.Column(db.String(80),unique=False)
    attachment = db.Column(db.String(80),unique =False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    steps = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name
        # return f'<User {self.username}>'

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

class BuildTestNoter(db.Model):
    version = db.Column(db.String(80),primary_key=True)
    releaseplan = db.Column(db.String(80),unique=False)
    testprocess = db.Column(db.String(80),unique=False)
    testcycle = db.Column(db.String(80),unique =False)
    issues = db.Column(db.String(80), unique=False, nullable=False)
    meeting = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class BuildORM(Resource):
    # 如果是get请求，认为是去查询所有case
    def get(self):
        app.logger.info(request.args)
        version_id = request.args.get("version")
        if version_id:
            version_data = BuildTestNoter.query.filter_by(id=version_id).first()
            versions = [version_data.as_dict()]
        else:
            version_data = BuildTestNoter.query.all()
            versions = [i.as_dict() for i in version_data]
            print(versions)
        return {"data": versions}

    # 如果是post请求，认为是去新增case
    def post(self):
        app.logger.info(request.args)
        app.logger.info(request.json)
        # 通过接口发送的数据进行TestCaseList类的实例化
        try:
            version = BuildTestNoter(**request.json)
            version.version = json.dumps(request.json.get("version"))
            app.logger.info(version)
            db.session.add(version)
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

class IssueLibrary(db.Model):

    id = db.Column(db.String(80),primary_key=True)
    reporter = db.Column(db.String(80),unique=False)
    date = db.Column(db.String(80),unique=False)
    severity = db.Column(db.String(80),unique =False,nullable=False)
    cyclename = db.Column(db.String(80), unique=False, nullable=False)
    regression = db.Column(db.String(3), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def insert_item(self,id):
        self.id = id
        if isinstance(self.id,int):
            self.id = str(self.id)



class IssueORM(Resource):
    # 如果是get请求，认为是去查询所有数据
    def get(self):
        app.logger.info(request.args)
        issue_id = request.args.get("issueid")
        if issue_id:
            issuelist = IssueLibrary.query.filter_by(reporter=issue_id).first()
            issue_list = [issuelist.as_dict()]
        else:
            issuelist = IssueLibrary.query.all()  # 获取数据库信息，显示在浏览器
            issue_list = [i.as_dict() for i in issuelist]
        return {"data": issue_list}

    # 如果是post请求，新增数据
    def post(self):
        app.logger.info(request.args)
        app.logger.info(request.json)

        try:
            issuelist = IssueLibrary(**request.json)
            issue_id = json.dumps(request.json.get("id"))
            app.logger.info(issue_id)
            IssueLibrary.insert_item(issue_id)
            db.session.add(issuelist)
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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # 允许上传的文件类型
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


class FileUploader(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, location='files')
        # self.parser.add_argument('filename',required=True, type=str, location='form')

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def uploaded_file(self,filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

    def post(self):
        # self.filename = filename
        args = self.parser.parse_args()
        print (args)
        file = args['file']
        if 'file' not in request.files:
            flash('no file part')
            # return redirect(request.url)
        # file =  request.files['file']
        # if file.filename == '':
        #     flash('no selected file')
        #     return redirect(request.url)
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # return redirect(url_for('uploaded_file', filename=filename))
            return {"message":"uploaded successfully"},200
        else:
            return {'message': 'File type not allowed'}, 400

    def get(self):
        return "ok,get it"
        # return send_from_directory(UPLOAD_FOLDER, filename)

# 注册到flask_restful api中去
api.add_resource(TestCaseServerORM, '/testcase_orm')
api.add_resource(FileUploader, '/upload')
api.add_resource(BuildORM, '/build_orm')
api.add_resource(IssueORM, '/issuelist')
# api.add_resource(UserIndex, '/index')
# api.add_resource(UserLogInORM, '/login')
# api.add_resource(UserLogOut, '/logout')



if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    # #     result = db.session.query(TestCase).all()
    # #     for item in result:
    # #         print(item)
    # admin('ruyu','1234')
    app.run(debug=True, use_reloader=True, port=5005)

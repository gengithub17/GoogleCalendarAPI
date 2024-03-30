from flask import Flask, render_template, request, redirect
import GoogleAPI as GA
import json
import datetime
import flask_login as flogin
from flask_apscheduler import APScheduler
import DataBase as DB
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
with open(GA.TOKEN_FILE, "r") as f:
	token = json.load(f)
	app.secret_key = token["refresh_token"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=15)
DB.db.init_app(app)

with app.app_context():
	DB.db.create_all()

login_manager = flogin.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return DB.LoginUser.query.get(int(user_id))
@login_manager.unauthorized_handler
def unauthorized_redirect():
	return redirect('/login')

@app.route('/', methods=['GET'])
@flogin.login_required
def mainpage():
	colorsdict = GA.color_info()
	return render_template("services/add.html", colors_json=json.dumps(colorsdict))

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		account = request.form['account']
		password = request.form['password']
		account_row = DB.LoginUser.query.filter_by(account=account, password=password).first()
		if account_row:
			flogin.login_user(account_row)
			return redirect('/')
		else:
			return render_template("login/login.html", message="認証エラー")
	else:
		return render_template("login/login.html")

@app.route('/post', methods=['POST'])
@flogin.login_required
def posted():
	form_data = request.form
	events = GA.Event.from_form(form_data)
	print(events)
	for event in events:
		GA.send(event)
	return redirect("/")

@app.errorhandler(HTTPException)
def handle_error(error:HTTPException):
		return render_template('error.html', error=error), error.code

if __name__ == '__main__':
	token_refresher = APScheduler()
	token_refresher.add_job(id="token_refresher", func=GA.authentication, trigger='interval', minutes=1)
	token_refresher.start()
	app.run(debug=True, host="0.0.0.0", port=8000)
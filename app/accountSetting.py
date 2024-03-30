from flask import Flask
import DataBase as DB
import json

def accountSetting():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
	DB.db.init_app(app)
	
	with open('.creds/account.json') as f:
		account_data = json.load(f)
		account = account_data["account"]
		password = account_data["password"]
	
	with app.app_context():
		DB.db.create_all()
		account_db = DB.LoginUser.query.filter_by(account=account).first()
		if account_db:
			account_db.password = password
		else:
			new_account = DB.LoginUser(account=account, password=password)
			DB.db.session.add(new_account)
		DB.db.session.commit()

if __name__ == "__main__":
	accountSetting()
# project/server/__init__.py

import os
import socket
import sys
import werkzeug
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

sys.path.append("project")
from project.server.auth.views import auth_blueprint
from project.server.oap.oapviews import oap_blueprint
from project.server.auth.flask_sso import SSO_APP
from project.server.oap.nickel.nickelviews import oap_nickel_blueprint

""" API definition """
werkzeug.cached_property = werkzeug.utils.cached_property
app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app=app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(oap_blueprint)
app.register_blueprint(SSO_APP)
app.register_blueprint(oap_nickel_blueprint)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
if __name__ == "__main__":
    """Start the application Server."""
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    app.run(host='0.0.0.0', port=8080, debug=True)
    #app.run(host=ipaddr, port=8191, threaded=True, ssl_context=('cert.pem', 'key.pem'))
    # app.run(debug=True)

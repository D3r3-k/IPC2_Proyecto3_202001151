from flask import Flask
from flask_cors import CORS
from controllers import main_bp, clientes_bp, bancos_bp

# ============== [ Base de Datos ] ==============
db_clientes = []
db_bancos = []

# ============== [ APP ] ==============
def create_app():
    app = Flask(__name__)
    app.config['db_clientes'] = db_clientes
    app.config['db_bancos'] = db_bancos

    app.register_blueprint(main_bp, url_prefix='/api/v1/')
    app.register_blueprint(clientes_bp, url_prefix='/api/v1/clientes')
    app.register_blueprint(bancos_bp, url_prefix='/api/v1/bancos')

    return app

app = create_app()
CORS(app)

# ============== [ MAIN ] ==============
if __name__ == '__main__':
    app.run(debug=True)

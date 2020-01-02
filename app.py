#!python
import os
from flask import Flask
from views.index import index_blueprint
from views.process import process_blueprint
from views.result import result_blueprint
app = Flask(__name__)

app.debug = True
app.templates_auto_reload=True

dirpath = os.getcwd()
foldername = os.path.basename(dirpath)

UPLOAD_FOLDER = foldername
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__))+"\\upload_folder"
app.config['ROOT_PATH'] = os.path.dirname(os.path.abspath(__file__))

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.register_blueprint(index_blueprint)
app.register_blueprint(process_blueprint)
app.register_blueprint(result_blueprint)



if __name__ == '__main__':
    app.run(debug=True)

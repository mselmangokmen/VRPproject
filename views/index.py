
import os
from flask import Flask, flash, request, redirect, render_template,Blueprint,url_for
from werkzeug.utils import secure_filename
from flask import current_app as app
import urllib
index_blueprint = Blueprint('index', __name__)




@index_blueprint.route('/')
def main():
    return render_template('index.html')


ALLOWED_EXTENSIONS = set(['xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@index_blueprint.route('/output')
def getOutout():
    content=""
    try:
        text = open('output', 'r+')
        content = text.read()
        text.close()
    except FileNotFoundError:
        return "File Not Found"
    return render_template('output.html', text=content)

@index_blueprint.route('/', methods=[ 'POST','GET'])
def startProcess():

    if request.method == 'POST':

        if 'dosya_koordinat' not in request.files and 'dosya_filo' not in request.files:
            return redirect(request.url)

        dosya_koordinat = request.files['dosya_koordinat']
        dosya_filo = request.files['dosya_filo']

        if dosya_koordinat.filename == '' or dosya_filo.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)

        if dosya_koordinat and allowed_file(dosya_koordinat.filename) and dosya_filo and allowed_file(dosya_filo.filename):
            filenameKoordinat = secure_filename(dosya_koordinat.filename)
            filenameFilo = secure_filename(dosya_filo.filename)
            dosya_koordinat.save(app.config['UPLOAD_FOLDER']+"\\"+filenameKoordinat)
            print("koordinat upload==> "+ app.config['UPLOAD_FOLDER']+"\\"+filenameKoordinat)
            dosya_filo.save(app.config['UPLOAD_FOLDER']+"\\"+filenameFilo)
            #flash('File successfully uploaded')
            alfa=request.form['tbAlfa']
            beta=request.form['tbBeta']
            omega=request.form['tbOmega']
            kontrol=request.form['tbKontrol']
            iterasyon=request.form['tbIterasyon']
            stopVal=request.form['tbStopVal']
            parameters={'file1':filenameKoordinat,'file2':filenameFilo,'alfa':alfa,'beta':beta,'omega':omega,'kontrol':kontrol,'iterasyon':iterasyon,'stopVal':stopVal}
            return redirect(url_for('process.main', parameters=parameters))
        else:
            flash('Lütfen sadece excel dosyalarını yükleyiniz')
            return redirect("/")
    elif request.method == 'GET':
            return redirect("/")
    else:
        return redirect("/")





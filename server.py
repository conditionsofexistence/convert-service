import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from converter.convert import convert
from converter.convert import ingest

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    #POST
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print filepath
            data, size, input_file = ingest(filepath, 'none')
            s = convert(data, size)
            return s
            #return redirect(url_for('index'))

    # GET
    return """
    <!doctype html>
    <title>CSV to TEI4BPS converter</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)

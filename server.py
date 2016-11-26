import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from converter.convert import convert
from converter.convert import ingest
import subprocess, uuid

UPLOAD_FOLDER = '/tmp/'
WORKSPACE_FOLDER = '/tmp/conversion'
ALLOWED_EXTENSIONS = set(['csv'])

if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WORKSPACE_FOLDER'] = WORKSPACE_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert(filepath, request):
    uid = uuid.uuid4().get_hex()
    header = "REQUESTED BY", request.remote_addr

    workspace = os.path.join(WORKSPACE_FOLDER, uid)
    os.makedirs(workspace)
    # copy filepath to worspace and invoke there
    print workspace
    out_path = os.path.join(workspace, 'output.xml')
    out, err = subprocess.Popen(['python','converter/convert.py', 
        '--input', filepath ,
        '--output', out_path, 
        '-p', 'none' ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    out = out.splitlines()
    err = [x.decode(encoding='ascii') for x in err.splitlines()]
    print len(err), type(err)
    print err
    #log = proc.stderr.read()
    print header
    return out_path, err, uid

@app.route('/download/<path:path>',  methods=['GET',])
def send_js(path):
    print path
    return send_from_directory(WORKSPACE_FOLDER, path)

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
            converted_file, log, uid= convert(filepath, request)

            ret = """
                <!doctype html>
                <head>
                <title>CSV to TEI4BPS converter | Conversion complete!</title>
                <h1>Conversion log</h1>
                <a href = "/download/{2}/output.xml"> File: {1}</a>
                <p style='font-family:"Andale Mono", "Monotype.com", monospace;'>{0}</p>""".format("<br/>".join([line for line in log]), converted_file, uid)
            return ret

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

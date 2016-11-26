import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from converter.convert import convert
from converter.convert import ingest
import subprocess, uuid

WORKSPACE_FOLDER = '/tmp/conversion'
ALLOWED_EXTENSIONS = set(['csv'])

if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

app = Flask(__name__)
app.config['WORKSPACE_FOLDER'] = WORKSPACE_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert(filepath, filename, request):
    out_path = os.path.join(filepath, 'output.xml')
    logfile = os.path.join(filepath, 'conversion.log')
    out, err = subprocess.Popen(['python','converter/convert.py',
        '--input', os.path.join(filepath, filename) ,
        '--output', out_path,
        '-p', 'none' ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    out = out.splitlines()
    err = [x.decode(encoding='ascii') for x in err.splitlines()]

    print len(err), type(err)

    with open(logfile, 'w+') as outfile:
        for line in err:
            outfile.write(line)

    return out_path, err

def make_workspace():
    uid = uuid.uuid4().get_hex()
    workspace = os.path.join(WORKSPACE_FOLDER, uid)
    os.makedirs(workspace)
    return workspace, uid

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
            filename = 'input.csv'#secure_filename(file.filename)
            workspace, uid = make_workspace()
            file.save(os.path.join(workspace, filename))
            filepath = os.path.join(workspace, filename)
            data, size, input_file = ingest(filepath, 'none')
            converted_file, log = convert(workspace, filename, request)

            ret = """
                <!doctype html>
                <html><head>
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on$
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7u$
                <title>CSV to TEI4BPS converter | Conversion complete!</title>
                </head><body>
             <div class="starter-template">
                <h1>Conversion log</h1>
                <div class="well">
                <a href = "/download/{2}/input.cav">Input file </a><br/>
                <a href = "/download/{2}/output.xml">Converted file </a><br/>
                <a href = "/download/{2}/conversion.log">This log</a>
                </div>
                <p style='font-family:"Andale Mono", "Monotype.com", monospace;'>{0}</p>
        </div></body></html>""".format("<br/>".join([line for line in log]), converted_file, uid)
            return ret

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
    <title>CSV to TEI4BPS converter</title>
    </head><body>
    <div class="container">
<div class="starter-template">
    <h1>CSV -> TEI4BPS Online Converter</h1>
    <p class="lead"> Select a CSV input file from your computer and click "upload" to have it converted in TEI4BPS</p>
    </div>
    <form class="form-inline" action="" method=post enctype=multipart/form-data>
         <div class="form-group">
         <input class="form-control" class="custom-file-input" type=file name=file>
         <input class="btn btn-primary" type=submit value=Upload>
    </div>
</form>
</div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
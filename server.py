import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
from converter.convert import convert
from converter.convert import ingest
import subprocess, uuid, datetime

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
    logfile_raw = os.path.join(filepath, 'raw-conversion.log')
    out = err = err_ret = None
    try:
        out, err = subprocess.Popen(['python','converter/convert.py',
            '--input', os.path.join(filepath, filename) ,
            '--output', out_path,
            '-p', 'none' ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        with open(logfile, 'w+') as outfile:
            outfile.write(err)
    except:
        pass

    with open(logfile, 'r') as logfile:
        err_ret = [x for x in logfile.readlines()]

    return out_path, err_ret


def make_workspace():
    uid = uuid.uuid4().get_hex()
    workspace = os.path.join(WORKSPACE_FOLDER, uid)
    os.makedirs(workspace)
    return workspace, uid

@app.route('/download/<path:path>',  methods=['GET',])
def send_js(path):
    return send_from_directory(WORKSPACE_FOLDER, path, mimetype='text/plain')


@app.route('/show/<path:path>',  methods=['GET',])
def show_path(path):
    filepath = os.path.join(WORKSPACE_FOLDER, path)

    modtime = datetime.datetime.fromtimestamp(
        os.path.getmtime(filepath)
    ).strftime('%Y-%m-%d %H:%M:%S')

    ctime = datetime.datetime.fromtimestamp(
        os.path.getctime(filepath)
    ).strftime('%Y-%m-%d %H:%M:%S')

    if os.path.exists(filepath):
        ret = render_template('task.html', task_id = path, m_time = modtime, c_time=ctime)
    else:
        ret = "Not found"
    return ret

@app.route('/list',  methods=['GET',])
def list():
    task_list = [x[1] for x in os.walk(WORKSPACE_FOLDER)][0]
    return render_template('list.html', task_list = task_list,)

@app.route("/", methods=['GET', 'POST'])
def index():
    #POST
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = 'input.csv' #secure_filename(file.filename)
            workspace, uid = make_workspace()
            filepath = os.path.join(workspace, filename)
            file.save(filepath)
            ret = uid
            try:
                data, size, input_file = ingest(filepath, 'none')
                converted_file, log = convert(workspace, filename, request)
                ret = render_template('task_complete.html', log = log,  task_id = uid, )
                return ret
            except Exception as e:
                return "http://convert.berkeleyprosopography.org/download/{0}/raw_output.txt\nError was: {1}".format(ret, e)
    
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
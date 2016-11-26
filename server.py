import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
import subprocess, uuid, datetime
import traceback

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

WORKSPACE_FOLDER = '/tmp/tasks'
ALLOWED_COMMANDS = ['w', 'hostname', 'time', 'ps', 'ps aux', 'ps axf', 'lsof -i', 'df -h', 'free -m']

if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

app = Flask(__name__)
app.config['WORKSPACE_FOLDER'] = WORKSPACE_FOLDER

def listify(command_string):
    ret = [x for x in command_string.split(' ')]
    return ret

def allowed_command(command):
    return command in ALLOWED_COMMANDS

def run(command, filepath, request):
    logfile = os.path.join(filepath, 'out.log')
    errfile = os.path.join(filepath, 'err.log')
    out = err = out_ret = err_ret = None
    try:
        out, err = subprocess.Popen(command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        with open(logfile, 'w+') as outfile:
            outfile.write(out)
        with open(errfile, 'w+') as outfile:
            outfile.write(err)
    except Exception as e:
        panicfile = os.path.join(workspace, "runtime-panic.log")
        with open(panicfile, 'w+') as outfile:
            outfile.write(traceback.format_exc())

    with open(logfile, 'r') as file:
        out_ret = [x for x in file.readlines()]
    with open(errfile, 'r') as file:
        out_err = [x for x in file.readlines()]
    return out_ret, err_ret


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
        tl = [x for x in os.walk(path)]
        ret = render_template('task.html', task_id = path, m_time = modtime, c_time=ctime,)
    else:
        ret = "Not found"
    return ret

@app.route('/list',  methods=['GET',])
def list():
    tl = [x for x in os.walk(WORKSPACE_FOLDER)]
    tk = {tl[0][1][i]: len(tl[i+1][2]) for i in range(0, len(tl)-1)}
    return render_template('list.html', task_list = tk,)

@app.route("/", methods=['GET', 'POST'])
def index():
    #POST
    if request.method == 'POST':
        print request.values
        print request.form
        print dir(request)
        command = listify(request.form['option'])
        if command and allowed_command(request.form['option']):
            workspace, uid = make_workspace()
            try:
                out = err =[]
                print "ABOUT TO RUN COMMAND", command
                out, err = run(command, workspace, request)
                ret = render_template('task_complete.html', err = err, out= out,  task_id = uid, )
                return ret
            except Exception as e:
                panicfile = os.path.join(workspace, "panic.log")
                with open(panicfile, 'w+') as outfile:
                    outfile.write(traceback.format_exc())
                ret = render_template('task_complete.html', 
                    log = [x for x in traceback.format_exc().split('\n')],  
                    task_id = uid, 
                    error = e )
                return ret
    
    return render_template('home.html', commands =ALLOWED_COMMANDS)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
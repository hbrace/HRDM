from flask import Flask, Response, render_template, redirect, url_for
import json
import docker
import subprocess

app = Flask(__name__)


@app.route('/list')
def checkContainers():
    client = docker.from_env()
    conList = []
    for cons in client.containers.list(all):
        if cons.status == 'running':
            status = 'stop'
        elif cons.status == 'exited':
            status = 'start'
        conList.append({'id': cons.id, 'name': cons.name, 'status': status})
    return render_template('list.html', listContainers=conList)


@app.route('/listOnly')
def checkContainersList():
    client = docker.from_env()
    conList = []
    for cons in client.containers.list():
        conList.append(cons.name)
    return str(conList)


@app.route('/start/<string:id>')
def startContainer(id):
    client = docker.from_env()
    con = client.containers.get(id)
    con.start()
    return redirect(url_for('checkContainers'))


@app.route('/stop/<string:id>')
def stopContainer(id):
    client = docker.from_env()
    con = client.containers.get(id)
    con.stop()
    return redirect(url_for('checkContainers'))


@app.route('/kill/<string:id>')
def killContainer(id):
    client = docker.from_env()
    con = client.containers.get(id)
    con.stop()
    con.remove()
    return redirect(url_for('checkContainers'))


@app.route('/restart/<string:id>')
def restartContainer(id):
    client = docker.from_env()
    con = client.containers.get(id)
    con.restart()
    return redirect(url_for('checkContainers'))


@app.route('/attributes/<string:id>')
def attributes(id):
    client = docker.from_env()
    con = client.containers.get(id)
    attrs = json.dumps(con.attrs, sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('attributes.html', containerDetails=attrs)


@app.route('/killall')
def killAll():
    client = docker.from_env()
    conList = client.containers.list()
    for con in conList:
        con.stop()
        con.remove()
    return redirect(url_for('checkContainers'))


@app.route('/start')
def startDockerDev():
    # TODO
    return redirect(url_for('checkContainers'))


@app.route('/logs/<string:id>')
def streamLogs(id):
    client = docker.from_env()
    con = client.containers.get(id)

    def generate():
        for line in con.logs(stream=True):
            yield line

    return Response(generate(), mimetype='text')

if __name__ =='__main__':
    app.run(debug=True, host='0.0.0.0')

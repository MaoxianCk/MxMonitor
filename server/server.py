import flask, json
from info import Info

server = flask.Flask(__name__)
sysInfo = Info()

@server.route('/')
def root():
    return flask.redirect(flask.url_for('info'), code=302)

@server.route('/info')
def info():
    return json.dumps(sysInfo.sysInfo, ensure_ascii=False)

if __name__ == '__main__':
    sysInfo.startUpdateSysInfo()
    # port可以指定端口，默认端口是5000
    # host默认是服务器，默认是127.0.0.1
    # debug=True 修改时不关闭服务
    server.run(host='0.0.0.0', port=7777, debug=True)

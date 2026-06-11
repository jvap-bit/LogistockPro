from flask import Flask
import subprocess, sys, os

app = Flask(__name__)

@app.route('/iniciar-sistema')
def iniciar():
    caminho = os.path.join(os.path.dirname(__file__), 'main.py')
    subprocess.Popen([sys.executable, caminho])
    return {'status': 'ok', 'mensagem': 'Sistema iniciado!'}

if __name__ == '__main__':
    app.run(port=5000)
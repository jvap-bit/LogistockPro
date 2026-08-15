from flask import Flask, jsonify, send_from_directory
import subprocess, sys, os, sqlite3, socket

from database import DB_PATH

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(os.path.dirname(BASE_DIR), "web")


@app.route('/iniciar-sistema')
def iniciar():
    caminho = os.path.join(os.path.dirname(__file__), 'main.py')
    subprocess.Popen([sys.executable, caminho])
    return {'status': 'ok', 'mensagem': 'Sistema iniciado!'}


@app.route('/api/pedido/<numero>')
def api_pedido(numero):
    """
    Consulta um pedido pelo número da OP (usado pelo leitor de QR Code
    do celular do entregador) e devolve os dados em JSON.
    """
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, numero, produto, quantidade, cliente, rua, casa, bairro, cep, prioridade, status "
            "FROM pedidos WHERE numero = ?",
            (numero,)
        )
        pedido = cur.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"encontrado": False, "erro": str(e)}), 500

    if not pedido:
        return jsonify({"encontrado": False}), 404

    _, numero, produto, quantidade, cliente, rua, casa, bairro, cep, prioridade, status = pedido
    return jsonify({
        "encontrado": True,
        "numero": numero,
        "produto": produto,
        "quantidade": quantidade,
        "cliente": cliente,
        "endereco": f"{rua}, {casa} - {bairro}",
        "cep": cep,
        "prioridade": prioridade,
        "status": status,
    })


@app.route('/leitor')
def leitor_entregador():
    """Serve a página mobile de leitura de QR Code para o entregador."""
    return send_from_directory(os.path.join(WEB_DIR, "pages"), "leitor-entregador.html")


def obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    ip_local = obter_ip_local()
    print("=" * 60)
    print(" LogiStock Pro - Servidor Web")
    print("=" * 60)
    print(f" No PC:      http://localhost:5000/leitor")
    print(f" No celular: http://{ip_local}:5000/leitor")
    print(" (celular precisa estar na mesma rede Wi-Fi do PC)")
    print("=" * 60)
    # host="0.0.0.0" permite acesso de outros dispositivos na mesma rede
    app.run(host="0.0.0.0", port=5000)

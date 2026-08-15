import sqlite3
import hashlib
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "arquivos_exportados")
DB_PATH = os.path.join(BASE_DIR, "producao.db")

if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    cursor = conn.cursor()
    # WAL reduz drasticamente os erros de "database is locked", permitindo
    # que leituras e escritas aconteçam ao mesmo tempo sem travar o arquivo.
    cursor.execute('PRAGMA journal_mode=WAL;')
    cursor.execute('PRAGMA busy_timeout=15000;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT, produto TEXT, quantidade TEXT,
            cliente TEXT, rua TEXT, casa TEXT, bairro TEXT, cep TEXT,
            prioridade TEXT, status TEXT, descricao TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT, acao TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            data_cadastro TEXT
        )
    ''')
    try:
        cursor.execute('ALTER TABLE pedidos ADD COLUMN descricao TEXT')
    except:
        pass
    conn.commit()
    conn.close()

def registrar_log(mensagem):
    conn = sqlite3.connect(DB_PATH, timeout=15)
    cursor = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cursor.execute("INSERT INTO logs (data_hora, acao) VALUES (?, ?)", (data_atual, mensagem))
    conn.commit()
    conn.close()

def cadastrar_usuario(email, senha, perfil):
    """Cadastra novo usuário. Retorna (True, msg) ou (False, msg)."""
    email = email.strip().lower()
    if not email or "@" not in email or "." not in email:
        return False, "E-mail inválido."
    if len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."
    perfis_validos = ["PCP", "Gestão", "Entregador", "Produção"]
    if perfil not in perfis_validos:
        return False, "Perfil inválido."
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15)
        cursor = conn.cursor()
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute(
            "INSERT INTO usuarios (email, senha, perfil, data_cadastro) VALUES (?, ?, ?, ?)",
            (email, hash_senha(senha), perfil, data_atual)
        )
        conn.commit()
        conn.close()
        registrar_log(f"Novo usuário cadastrado: {email} | Perfil: {perfil}")
        return True, "Cadastro realizado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Este e-mail já está cadastrado."
    except Exception as e:
        return False, f"Erro ao cadastrar: {e}"

def autenticar_usuario(email, senha):
    """Autentica usuário. Retorna (True, perfil) ou (False, None)."""
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH, timeout=15)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT perfil FROM usuarios WHERE email = ? AND senha = ?",
        (email, hash_senha(senha))
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return True, resultado[0]
    return False, None

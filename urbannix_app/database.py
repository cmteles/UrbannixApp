"""
database.py
Camada de acesso ao banco de dados SQLite da Urbannix.
Todas as funções de leitura/escrita no banco ficam centralizadas aqui.
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "urbannix.db"


@contextmanager
def get_conn():
    """Abre conexão com o banco e garante que ela é fechada no final."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Cria as tabelas se ainda não existirem. Chamada uma vez ao iniciar o app."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                endereco TEXT,
                criado_em TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco_unitario REAL NOT NULL DEFAULT 0,
                estoque_atual INTEGER NOT NULL DEFAULT 0,
                estoque_minimo INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                data TEXT DEFAULT (datetime('now')),
                status TEXT NOT NULL DEFAULT 'Pendente',
                observacoes TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            );

            CREATE TABLE IF NOT EXISTS orcamento_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            );
            """
        )


# ---------- CLIENTES ----------

def add_cliente(nome, telefone="", endereco=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)",
            (nome, telefone, endereco),
        )


def get_clientes():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()


# ---------- PRODUTOS / ESTOQUE ----------

def add_produto(nome, descricao, preco_unitario, estoque_atual, estoque_minimo=0):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO produtos (nome, descricao, preco_unitario, estoque_atual, estoque_minimo)
               VALUES (?, ?, ?, ?, ?)""",
            (nome, descricao, preco_unitario, estoque_atual, estoque_minimo),
        )


def get_produtos():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM produtos ORDER BY nome").fetchall()


def ajustar_estoque(produto_id, quantidade_delta):
    """Soma (ou subtrai, se negativo) a quantidade informada ao estoque atual."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
            (quantidade_delta, produto_id),
        )


# ---------- ORÇAMENTOS ----------

def criar_orcamento(cliente_id, itens, observacoes=""):
    """
    itens: lista de dicts [{produto_id, quantidade, preco_unitario}, ...]
    Cria o orçamento, os itens, e dá baixa no estoque.
    Retorna o id do orçamento criado.
    """
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO orcamentos (cliente_id, observacoes) VALUES (?, ?)",
            (cliente_id, observacoes),
        )
        orcamento_id = cur.lastrowid

        for item in itens:
            conn.execute(
                """INSERT INTO orcamento_itens (orcamento_id, produto_id, quantidade, preco_unitario)
                   VALUES (?, ?, ?, ?)""",
                (orcamento_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            conn.execute(
                "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        return orcamento_id


def get_orcamentos():
    with get_conn() as conn:
        return conn.execute(
            """SELECT o.id, o.data, o.status, c.nome AS cliente_nome
               FROM orcamentos o
               JOIN clientes c ON c.id = o.cliente_id
               ORDER BY o.data DESC"""
        ).fetchall()


def get_orcamento_detalhado(orcamento_id):
    with get_conn() as conn:
        orcamento = conn.execute(
            """SELECT o.*, c.nome AS cliente_nome, c.telefone AS cliente_telefone
               FROM orcamentos o
               JOIN clientes c ON c.id = o.cliente_id
               WHERE o.id = ?""",
            (orcamento_id,),
        ).fetchone()

        itens = conn.execute(
            """SELECT oi.*, p.nome AS produto_nome
               FROM orcamento_itens oi
               JOIN produtos p ON p.id = oi.produto_id
               WHERE oi.orcamento_id = ?""",
            (orcamento_id,),
        ).fetchall()

        return orcamento, itens


def atualizar_status_orcamento(orcamento_id, novo_status):
    with get_conn() as conn:
        conn.execute(
            "UPDATE orcamentos SET status = ? WHERE id = ?", (novo_status, orcamento_id)
        )

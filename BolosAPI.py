from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

#--------------------------------------------------------------
#--------------------------------------------------------------
#--------EXECUT AVIA TERMINAL
#--------python BolosAPI.py
#--------QUANDO EXECUTAR ABRIR A URL NO NAVEGADOR
#--------NO FINAL DA URL COLOCAR AS ROTAS (GET/CLIENTES, POST/CLIENTES, GET/PRODUTOS,ETC)
#--------------------------------------------------------------
#--------------------------------------------------------------

def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='bolosdepote'
    )
    
# TUDO CRIADO PELO POST, PARA CHECAR NO GET, VA ATE AS ULTIMAS REQUISIÇÕES, LÁ ESTARÃO

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ID_CLIENTE, NOME, TELEFONE, EMAIL FROM CLIENTE")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(clientes)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/clientes', methods=['POST'])
def criar_cliente():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CLIENTE (NOME, TELEFONE, EMAIL) 
            VALUES (%s, %s, %s)
        """, (dados['nome'], dados['telefone'], dados.get('email')))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Cliente criado com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@app.route('/enderecos', methods=['POST'])
def criar_endereco():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ENDERECO_CLIENTE 
            (ID_CLIENTE, RUA, NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, CEP, PRINCIPAL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            dados['id_cliente'], dados['rua'], dados['numero'], dados.get('complemento'),
            dados['bairro'], dados['cidade'], dados['estado'], dados['cep'], dados.get('principal', False)
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Endereço cadastrado com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    
@app.route('/enderecos', methods=['GET'])
def listar_enderecos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.ID_ENDERECO, e.ID_CLIENTE, c.NOME AS CLIENTE, 
                   e.RUA, e.NUMERO, e.COMPLEMENTO, e.BAIRRO, e.CIDADE, 
                   e.ESTADO, e.CEP, e.PRINCIPAL
            FROM ENDERECO_CLIENTE e
            JOIN CLIENTE c ON e.ID_CLIENTE = c.ID_CLIENTE
        """)
        enderecos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(enderecos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ID_PRODUTO, NOME, DESCRICAO, PRECO FROM PRODUTO")
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        for p in produtos:
            p['PRECO'] = float(p['PRECO'])
        return jsonify(produtos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    
@app.route('/produtos', methods=['POST'])
def criar_produto():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PRODUTO 
            (NOME, DESCRICAO, PRECO, DATA_FABRICACAO, TEMPO_VALIDADE_DIAS)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            dados['nome'], dados.get('descricao'), dados['preco'], 
            dados.get('data_fabricacao'), dados['tempo_validade_dias']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Produto criado com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        sql = """
            INSERT INTO PEDIDO (ID_CLIENTE, ID_PRODUTO, QUANTIDADE, PRECO_UNITARIO, STATUS, OBSERVACOES)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            dados['id_cliente'],
            dados['id_produto'],
            dados['quantidade'],
            dados['preco_unitario'],
            dados.get('status', 'AGUARDANDO'),
            dados.get('observacoes')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Pedido criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/pagamentos', methods=['POST'])
def criar_pagamento():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PAGAMENTO 
            (ID_PEDIDO, FORMA_PAGAMENTO, STATUS_PAGAMENTO, VALOR_PAGO, DATA_PAGAMENTO, CODIGO_TRANSACAO)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            dados['id_pedido'], dados['forma_pagamento'], dados.get('status_pagamento', 'PENDENTE'),
            dados['valor_pago'], dados.get('data_pagameto'), dados.get('codigo_transacao')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Pagamento registrado com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    
@app.route('/pagamentos', methods=['GET'])
def listar_pagamentos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.ID_PAGAMENTO, p.ID_PEDIDO, c.NOME AS CLIENTE, 
                   pr.NOME AS PRODUTO, p.FORMA_PAGAMENTO, 
                   p.STATUS_PAGAMENTO, p.VALOR_PAGO, 
                   p.DATA_PAGAMENTO, p.CODIGO_TRANSACAO
            FROM PAGAMENTO p
            JOIN PEDIDO pd ON pd.ID_PEDIDO = p.ID_PEDIDO
            JOIN CLIENTE c ON c.ID_CLIENTE = pd.ID_CLIENTE
            JOIN PRODUTO pr ON pr.ID_PRODUTO = pd.ID_PRODUTO
        """)
        pagamentos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(pagamentos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/estoque', methods=['POST'])
def adicionar_estoque():
    try:
        dados = request.json
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ESTOQUE (ID_PRODUTO, QUANTIDADE_DISPONIVEL)
            VALUES (%s, %s)
        """, (
            dados['id_produto'], dados['quantidade_disponivel']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Estoque adicionado com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/estoque', methods=['GET'])
def listar_estoque():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.ID_PRODUTO, p.NOME, e.QUANTIDADE_DISPONIVEL
            FROM ESTOQUE e
            JOIN PRODUTO p ON e.ID_PRODUTO = p.ID_PRODUTO
        """)
        estoque = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(estoque)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/estoque/<int:id_produto>', methods=['PUT'])
def atualizar_estoque(id_produto):
    try:
        dados = request.json
        nova_qtd = dados.get('quantidade')
        if nova_qtd is None:
            return jsonify({"erro": "O campo 'quantidade' é obrigatório."}), 400

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ESTOQUE SET QUANTIDADE_DISPONIVEL = %s 
            WHERE ID_PRODUTO = %s
        """, (nova_qtd, id_produto))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Estoque atualizado com sucesso."})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/relatorio/comprovantes', methods=['GET'])
def comprovantes_pedido():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ComprovantePedido")
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
from datetime import datetime
from flask import jsonify

currentDateTime = datetime.now()
 
app = Flask(__name__)
app.secret_key = "desafio-serasa"
 
DB_HOST = "db"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "123"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
@app.route('/')
def Index():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM USUARIOS") 
        cur.fetchall()
        return render_template('index.html')

@app.get('/usuarios/listar')
def Listar():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM USUARIOS") 
        list_users = cur.fetchall()
        return render_template('./usuarios/listar_usuarios.html', list_users = list_users)

@app.get('/usuarios/json')
def ListarJSON():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT ID, NAME AS NOME, CPF, EMAIL, PHONE_NUMBER AS TELEFONE, CREATED_AT AS CRIADO_EM, UPDATED_AT AS ULTIMO_UPDATE FROM USUARIOS") 
        list_users = [dict(d) for d in cur.fetchall()]
        return jsonify(list_users)

@app.get('/pedidos/listar')
def ListarPedidos():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM PEDIDOS")
        list_pedidos = cur.fetchall()
        return render_template('./pedidos/listar_pedidos.html', list_pedidos = list_pedidos)

@app.get('/pedidos/json')
def ListarPedidosJSON():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT ID, USER_ID AS ID_USUARIO, ITEM_DESCRIPTION AS DESCRICAO_ITEM, ITEM_PRICE AS PRECO, ITEM_QUANTITY AS QUANTIDADE, TOTAL_VALUE AS VALOR_TOTAL, CREATED_AT AS CRIADO_EM, UPDATED_AT AS ULTIMO_UPDATE FROM PEDIDOS") 
        list_pedidos = [dict(d) for d in cur.fetchall()]
        return jsonify(list_pedidos)

@app.route('/usuarios/cadastrar')
def Cadastrar_Usuarios():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM USUARIOS") 
        list_users = cur.fetchall()
        return render_template('./usuarios/cadastrar_usuarios.html', list_users = list_users)

@app.route('/pedidos/cadastrar')
def cadastrar_pedidos():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM PEDIDOS") 
        list_pedidos = cur.fetchall()
        return render_template('./pedidos/cadastrar_pedidos.html', list_pedidos = list_pedidos)
 
@app.post('/usuarios/add')
def add_usuario():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        name = request.form['name']
        cpf = request.form['cpf']
        email = request.form['email']
        phone_number = request.form['phone_number']
        currentDateTime = datetime.now()
        created_at = currentDateTime
        updated_at = currentDateTime
        cur.execute(f"SELECT CPF FROM USUARIOS WHERE CPF = '{cpf}' LIMIT 1")
        validation = str(cur.fetchone()).replace("[", "").replace("]", "").replace("'", "")
        if validation == cpf:
            flash('CPF já cadastrado no banco!')
            return redirect(url_for('Cadastrar_Usuarios'))
        else:
            cur.execute("INSERT INTO USUARIOS (name, cpf, email, phone_number, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s)", (name, cpf, email, phone_number, created_at, updated_at))
            conn.commit()
            flash('Usuário adicionado com sucesso!')
            return redirect(url_for('Listar'))

@app.post('/pedidos/add')
def add_pedidos():
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        item_description = request.form['item_description']
        user_id = request.form['user_id']
        item_quantity = request.form['item_quantity']
        item_price = request.form['item_price']
        total_value = request.form['total_value']
        currentDateTime = datetime.now()
        created_at = currentDateTime
        updated_at = currentDateTime
        cur.execute(f"SELECT ID FROM USUARIOS WHERE ID = '{user_id}' LIMIT 1")
        validation_pedido = str(cur.fetchone()).replace("[", "").replace("]", "").replace("'", "")
        if validation_pedido == "None":
            flash('ID de usuário não existente!')
            return redirect(url_for('ListarPedidos'))
        else:
            cur.execute("INSERT INTO PEDIDOS (item_description, user_id, item_quantity, item_price, total_value, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s)", (item_description, user_id, item_quantity, item_price, total_value, created_at, updated_at))
            conn.commit()
            flash('Pedido adicionado com sucesso!')
            return redirect(url_for('ListarPedidos'))
 
@app.route('/usuarios/edit/<id>', methods = ['POST', 'GET'])
def edit_usuario(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute('SELECT * FROM USUARIOS WHERE id = {0}'.format(id))
        data = cur.fetchall()
        cur.close()
        print(data[0])
        return render_template('./usuarios/edit_usuarios.html', usuario = data[0])

@app.route('/pedidos/edit/<id>', methods = ['POST', 'GET'])
def edit_pedido(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute('SELECT * FROM PEDIDOS WHERE id = {0}'.format(id))
        data = cur.fetchall()
        cur.close()
        return render_template('./pedidos/edit_pedidos.html', pedido = data[0])
 
@app.post('/usuarios/update/<id>')
def update_usuario(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        name = request.form['name']
        cpf = request.form['cpf']
        email = request.form['email']
        currentDateTime = datetime.now()
        updated_at = currentDateTime
        cur.execute(f"SELECT CPF FROM USUARIOS WHERE CPF = '{cpf}' AND ID <> {id} LIMIT 1")
        validation = str(cur.fetchone()).replace("[", "").replace("]", "").replace("'", "")
        if validation == cpf:
            flash('CPF já cadastrado no banco!')
            return redirect(url_for('Cadastrar_Usuarios'))
        else:
            cur.execute("""
                UPDATE USUARIOS
                SET name = %s,
                    cpf = %s,
                    email = %s,
                    updated_at = %s
                WHERE id = %s
            """, (name, cpf, email, updated_at, id))
            flash('Usuário alterado com sucesso!')
            conn.commit()
            return redirect(url_for('Listar'))
    
@app.post('/pedidos/update/<id>')
def update_pedido(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        item_description = request.form['item_description']
        user_id = request.form['user_id']
        item_quantity = request.form['item_quantity']
        item_price = request.form['item_price']
        total_value = request.form['total_value']
        currentDateTime = datetime.now()
        updated_at = currentDateTime
        cur.execute(f"SELECT ID FROM USUARIOS WHERE ID = '{user_id}' LIMIT 1")
        validation_pedido = str(cur.fetchone()).replace("[", "").replace("]", "").replace("'", "")
        if validation_pedido == "None":
            flash('ID de usuário não existente!')
            return redirect(url_for('ListarPedidos'))
        else:
            cur.execute("""
                UPDATE PEDIDOS
                SET item_description = %s,
                    user_id = %s,
                    item_quantity = %s,
                    item_price = %s,
                    total_value = %s,
                    updated_at = %s
                WHERE id = %s
            """, (item_description, user_id, item_quantity, item_price, total_value, updated_at, id))
            flash('Pedido alterado com sucesso!')
            conn.commit()
            return redirect(url_for('ListarPedidos'))
 
@app.route('/usuarios/delete/<id>', methods = ['POST','GET'])
def delete_usuario(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute('DELETE FROM USUARIOS WHERE id = {0}'.format(id))
        conn.commit()
        flash('Registro removido com sucesso.')
        return redirect(url_for('Listar'))

@app.route('/pedidos/delete/<id>', methods = ['POST','GET'])
def delete_pedido(id):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute('DELETE FROM PEDIDOS WHERE id = {0}'.format(id))
        conn.commit()
        flash('Registro removido com sucesso.')
        return redirect(url_for('ListarPedidos'))
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
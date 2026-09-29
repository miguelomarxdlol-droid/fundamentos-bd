from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="121212",  # Coloca tu contraseña si la cambiaste
        database="Cafeteria_Universitaria"
    )
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_producto AS ID_Producto, nombre AS Nombre, categoria AS Categoria, precio AS Precio, stock AS Stock FROM Producto")
    lista_productos = cursor.fetchall()
    cursor.close()  
    conn.close()
    return render_template('productos.html', productos=lista_productos)

@app.route('/pedidos')
def pedidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            p.id_pedido AS ID_Pedido,
            c.nombre AS Cliente,
            p.fecha_pedido AS Fecha,
            p.estado AS Estado,
            IFNULL(SUM(CAST(dp.cantidad AS DECIMAL(10,2)) * CAST(dp.precio_unitario AS DECIMAL(10,2))), 0.00) AS Total
        FROM Pedido p
        LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
        LEFT JOIN Detalle_Pedido dp ON p.id_pedido = dp.id_pedido
        GROUP BY p.id_pedido, c.nombre, p.fecha_pedido, p.estado
    """
    cursor.execute(query)
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', pedidos=lista_pedidos)

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        categoria = request.form.get('categoria') or 'General'
        precio = request.form.get('precio')
        stock = request.form.get('stock')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO producto (nombre, categoria, precio, stock)
            VALUES (%s, %s, %s, %s)
        """, (nombre, categoria, precio, stock))
        
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/productos')

    return render_template('agregar_producto.html')

@app.route('/agregar_pedido', methods=['GET', 'POST'])
def agregar_pedido():
    conn = get_db_connection()

    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        fecha = request.form.get('fecha')
        estado = request.form.get('estado')
        id_producto = request.form.get('id_producto')
        cantidad = request.form.get('cantidad')

        cursor = conn.cursor(dictionary=True)

        # 1. Obtener el precio unitario del producto seleccionado
        cursor.execute("SELECT precio FROM producto WHERE id_producto = %s", (id_producto,))
        prod = cursor.fetchone()
        precio_unitario = prod['precio'] if prod else 0.00

        # 2. Insertar el registro principal en la tabla 'pedido'
        cursor.execute("""
            INSERT INTO pedido (id_cliente, fecha_pedido, estado)
            VALUES (%s, %s, %s)
        """, (id_cliente, fecha, estado))
        
        # Obtener el ID generado para este nuevo pedido
        id_nuevo_pedido = cursor.lastrowid

        # 3. Insertar el ítem en la tabla 'detalle_pedido'
        cursor.execute("""
            INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (id_nuevo_pedido, id_producto, cantidad, precio_unitario))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/pedidos')

    # GET: Cargar listas de clientes y productos para los desplegables <select>
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_cliente, nombre FROM cliente")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre, precio FROM producto")
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('agregar_pedido.html', clientes=clientes, productos=productos)

@app.route('/actualizar_producto/<int:id>', methods=['GET', 'POST'])
def actualizar_producto(id):
    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        stock = request.form.get('stock')

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE producto 
            SET nombre = %s, precio = %s, stock = %s 
            WHERE id_producto = %s
        """, (nombre, precio, stock, id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/productos')

    # GET: Carga los datos del producto seleccionado
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()

    # Apunta al nombre de tu archivo HTML (en plural según tus archivos)
    return render_template('actualizar_productos.html', producto=producto)



@app.route('/actualizar_pedido/<int:id>', methods=['GET', 'POST'])
def actualizar_pedido(id):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="121212",
        database="cafeteria_universitaria"
    )

    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        fecha_pedido = request.form.get('fecha_pedido')
        estado = request.form.get('estado')

        cursor = conexion.cursor()
        # Solo actualizamos las columnas reales de la tabla 'pedido'
        cursor.execute("""
            UPDATE pedido 
            SET id_cliente = %s, fecha_pedido = %s, estado = %s 
            WHERE id_pedido = %s
        """, (id_cliente, fecha_pedido, estado, id))
        
        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect('/pedidos')

    # Petición GET
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pedido WHERE id_pedido = %s", (id,))
    pedido = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template('actualizar_pedido.html', pedido=pedido)



@app.route('/borrar_producto/<int:id_producto>', methods=['POST'])
def borrar_producto(id_producto):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Producto WHERE id_producto = %s", (id_producto,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/productos')

@app.route('/borrar_pedido/<int:id_pedido>', methods=['POST'])
def borrar_pedido(id_pedido):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pedido WHERE id_pedido = %s", (id_pedido,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/pedidos')






if __name__ == '__main__':
    app.run(debug=True)
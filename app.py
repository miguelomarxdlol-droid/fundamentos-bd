from flask import Flask, render_template
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
    
    # CAST convierte los textos VARCHAR a números DECIMAL/DECIMAL para la multiplicación
    query = """
        SELECT 
            p.id_pedido AS ID_Pedido,
            c.nombre AS Cliente,
            p.fecha_pedido AS Fecha,
            p.estado AS Estado,
            SUM(CAST(dp.cantidad AS DECIMAL(10,2)) * CAST(dp.precio_unitario AS DECIMAL(10,2))) AS Total
        FROM Pedido p
        JOIN Cliente c ON p.id_cliente = c.id_cliente
        JOIN Detalle_Pedido dp ON p.id_pedido = dp.id_pedido
        GROUP BY p.id_pedido, c.nombre, p.fecha_pedido, p.estado
    """
    cursor.execute(query)
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pedidos.html', pedidos=lista_pedidos)

if __name__ == '__main__':
    app.run(debug=True)
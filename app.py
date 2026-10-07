import os
import pymysql
from flask import Flask, render_template, render_template_string, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

USER = "root"
PASSWORD = "121212"
HOST = "localhost"
PORT = 3306
DB_NAME = "practica2.2"

try:
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`;")
    connection.close()
except Exception as e:
    print(f"Error MySQL: {e}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS
# ==========================================

class Coordinador(db.Model):
    __tablename__ = 'coordinador'
    id_coordinador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_coordinador = db.Column(db.String(45), nullable=True)

class Carrera(db.Model):
    __tablename__ = 'carrera'
    id_carrera = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrera = db.Column(db.String(100), nullable=True)
    coordinador_id_coordinador = db.Column(db.Integer, db.ForeignKey('coordinador.id_coordinador'), nullable=False)

class Alumnos(db.Model):
    __tablename__ = 'Alumnos'
    id_Alumnos = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=True)
    carrera_id_carrera = db.Column(db.Integer, db.ForeignKey('carrera.id_carrera'), nullable=False)

class Materia(db.Model):
    __tablename__ = 'Materia'
    id_materia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_materia = db.Column(db.String(100), nullable=True)

class Inscripcion(db.Model):
    __tablename__ = 'inscripcion'
    id_inscripcion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Alumnos_id_Alumnos = db.Column(db.Integer, db.ForeignKey('Alumnos.id_Alumnos'), nullable=False)
    Materia_id_materia = db.Column(db.Integer, db.ForeignKey('Materia.id_materia'), nullable=False)

with app.app_context():
    db.create_all()

# ==========================================
# RUTAS DE NAVEGACIÓN Y VISTAS
# ==========================================

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Inicio</title></head>
    <body>
        <h1>Sistema de Gestión Escolar</h1><hr>
        <ul>
            <li><a href="/coordinador">Coordinadores</a></li>
            <li><a href="/carrera">Carreras</a></li>
            <li><a href="/alumnos">Alumnos</a></li>
            <li><a href="/materia">Materias</a></li>
            <li><a href="/inscripcion">Inscripciones</a></li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(html)

# --- COORDINADOR ---
@app.route('/coordinador', methods=['GET', 'POST'])
def coordinador():
    if request.method == 'POST':
        nombre = request.form.get('nombre_coordinador')
        if nombre:
            nuevo = Coordinador(nombre_coordinador=nombre)
            db.session.add(nuevo)
            db.session.commit()
        return redirect(url_for('coordinador'))
    return render_template('coordinador.html', coordinadores=Coordinador.query.all())

@app.route('/editar_coordinador/<int:id>', methods=['POST'])
def editar_coordinador(id):
    item = Coordinador.query.get_or_404(id)
    item.nombre_coordinador = request.form.get('nombre_coordinador')
    db.session.commit()
    return jsonify({"status": "success", "message": "Coordinador actualizado correctamente"})

@app.route('/eliminar_coordinador/<int:id>')
def eliminar_coordinador(id):
    item = Coordinador.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('coordinador'))

# --- CARRERA ---
@app.route('/carrera', methods=['GET', 'POST'])
def carrera():
    if request.method == 'POST':
        nombre = request.form.get('carrera')
        id_coord = request.form.get('coordinador_id')
        if nombre and id_coord:
            nueva = Carrera(carrera=nombre, coordinador_id_coordinador=id_coord)
            db.session.add(nueva)
            db.session.commit()
        return redirect(url_for('carrera'))
    return render_template('carrera.html', carreras=Carrera.query.all(), coordinadores=Coordinador.query.all())

@app.route('/editar_carrera/<int:id>', methods=['POST'])
def editar_carrera(id):
    item = Carrera.query.get_or_404(id)
    item.carrera = request.form.get('carrera')
    item.coordinador_id_coordinador = request.form.get('coordinador_id')
    db.session.commit()
    return jsonify({"status": "success", "message": "Carrera actualizada correctamente"})

@app.route('/eliminar_carrera/<int:id>')
def eliminar_carrera(id):
    item = Carrera.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('carrera'))

# --- ALUMNOS ---
@app.route('/alumnos', methods=['GET', 'POST'])
def alumnos():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        id_carrera = request.form.get('carrera_id')
        if nombre and id_carrera:
            nuevo = Alumnos(nombre=nombre, carrera_id_carrera=id_carrera)
            db.session.add(nuevo)
            db.session.commit()
        return redirect(url_for('alumnos'))
    return render_template('Alumnos.html', alumnos=Alumnos.query.all(), carreras=Carrera.query.all())

@app.route('/editar_alumno/<int:id>', methods=['POST'])
def editar_alumno(id):
    item = Alumnos.query.get_or_404(id)
    item.nombre = request.form.get('nombre')
    item.carrera_id_carrera = request.form.get('carrera_id')
    db.session.commit()
    return jsonify({"status": "success", "message": "Alumno actualizado correctamente"})

@app.route('/eliminar_alumno/<int:id>')
def eliminar_alumno(id):
    item = Alumnos.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('alumnos'))

# --- MATERIA ---
@app.route('/materia', methods=['GET', 'POST'])
def materia():
    if request.method == 'POST':
        nombre = request.form.get('nombre_materia')
        if nombre:
            nueva = Materia(nombre_materia=nombre)
            db.session.add(nueva)
            db.session.commit()
        return redirect(url_for('materia'))
    return render_template('Materia.html', materias=Materia.query.all())

@app.route('/editar_materia/<int:id>', methods=['POST'])
def editar_materia(id):
    item = Materia.query.get_or_404(id)
    item.nombre_materia = request.form.get('nombre_materia')
    db.session.commit()
    return jsonify({"status": "success", "message": "Materia actualizada correctamente"})

@app.route('/eliminar_materia/<int:id>')
def eliminar_materia(id):
    item = Materia.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('materia'))

# --- INSCRIPCION ---
@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    if request.method == 'POST':
        id_alumno = request.form.get('alumno_id')
        id_materia = request.form.get('materia_id')
        if id_alumno and id_materia:
            nueva = Inscripcion(Alumnos_id_Alumnos=id_alumno, Materia_id_materia=id_materia)
            db.session.add(nueva)
            db.session.commit()
        return redirect(url_for('inscripcion'))
    return render_template('inscripcion.html', inscripciones=Inscripcion.query.all(), alumnos=Alumnos.query.all(), materias=Materia.query.all())

@app.route('/editar_inscripcion/<int:id>', methods=['POST'])
def editar_inscripcion(id):
    item = Inscripcion.query.get_or_404(id)
    item.Alumnos_id_Alumnos = request.form.get('alumno_id')
    item.Materia_id_materia = request.form.get('materia_id')
    db.session.commit()
    return jsonify({"status": "success", "message": "Inscripción actualizada correctamente"})

@app.route('/eliminar_inscripcion/<int:id>')
def eliminar_inscripcion(id):
    item = Inscripcion.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('inscripcion'))

if __name__ == '__main__':
    app.run(debug=True)
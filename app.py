from flask import Flask
from flask import render_template
from flaskext.mysql import MySQL
from flask import request
from flask import redirect
from flask import send_from_directory
from flask import url_for
from datetime import datetime
from flask import flash
import os

# instancio una clase de flask
app = Flask(__name__)
app.secret_key = 'Clave'
mysql = MySQL()
CARPETA = os.path.join('uploads')
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_BD'] = 'apppeliculas'
app.config['CARPETA'] = CARPETA
mysql.init_app(app)


@app.route('/')
def index():
    sql = '''SELECT * FROM apppeliculas.peliculas;'''
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    peliculas = cursor.fetchall()

    return render_template('peliculas/index.html', peliculas=peliculas)

# RUTA PARA CREATE FORM


@app.route('/create')
def create():
    return render_template('peliculas/create.html')


@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    _foto = request.files['txtFoto']

    if _nombre == '' or _descripcion == '' or _foto.filename == '':
         flash('Ingresar todos los datos.')
         return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime('%Y%m%d%H%M%S')
    nuevo_nombre_foto = ''
    if _foto.filename != '':
        nuevo_nombre_foto = tiempo + _foto.filename
        _foto.save('uploads/' + nuevo_nombre_foto)

    sql = '''INSERT INTO apppeliculas.peliculas
        (`nombre`,
        `foto`,
        `descripcion`)
         VALUES
        (%s,
        %s,
        %s);
        '''
    datos = (_nombre, nuevo_nombre_foto, _descripcion)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    # Commit cuando voy a modificar la base de datos
    conn.commit()
    return redirect('/')


@app.route('/destroy/<int:id>')
def destroy(id):
    sql = 'DELETE FROM apppeliculas.peliculas WHERE id = %s'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT foto FROM apppeliculas.`peliculas` WHERE id=%s', (id))
    foto_ant = cursor.fetchone()
    os.remove(os.path.join(app.config['CARPETA'], foto_ant[0]))
    cursor.execute(sql, (id))
    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):

    sql = 'SELECT * FROM apppeliculas.peliculas WHERE id=%s;'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, (id))
    pelicula = cursor.fetchone()

    return render_template('peliculas/edit.html', pelicula=pelicula)


@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _descripcion = request.form['txtDescripcion']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = '''
    UPDATE apppeliculas.`peliculas`
    SET
    `nombre`= %s,
    `descripcion` = %s
    WHERE `id` = %s;  
    '''
    datos = (_nombre, _descripcion, id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    now = datetime.now()
    tiempo = now.strftime('%Y%m%d%H%M%S')
    nuevo_nombre_foto = ''
    if _foto.filename != '':
        nuevo_nombre_foto = tiempo + _foto.filename
        _foto.save('uploads/' + nuevo_nombre_foto)

        cursor.execute('SELECT foto FROM apppeliculas.`peliculas` WHERE id=%s', (id))
        foto_ant = cursor.fetchone()
        os.remove(os.path.join(app.config['CARPETA'], foto_ant[0]))
        
        cursor.execute('UPDATE apppeliculas.peliculas SET foto =%s WHERE id=%s', (nuevo_nombre_foto, id))
        conn.commit()

    return redirect('/')
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

if __name__ == '__main__':
    app.run(debug=True)

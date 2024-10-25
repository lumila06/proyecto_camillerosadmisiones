import os
from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)

# Permitir solicitudes CORS desde cualquier origen
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'password'),
    'database': os.getenv('DB_NAME', 'gestion')
}

# Conexión a la base de datos MySQL
try:
    db = mysql.connector.connect(**db_config)
except mysql.connector.Error as err:
    print(f"Error al conectar a la base de datos: {err}")
    db = None  # Define db como None en caso de error

# Ruta para obtener la lista de pacientes admitidos
@app.route('/admitted-patients', methods=['GET'])
def get_admitted_patients():
    if db is None:
        return jsonify({'error': 'No se puede conectar a la base de datos'}), 500

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT nombre, apellido, dni, sexo, edad, codigo, ubicacion FROM admisiones")
    patients = cursor.fetchall()
    cursor.close()
    return jsonify(patients)

# Ruta para agregar o actualizar un paciente
@app.route('/add-or-update-patient', methods=['POST'])
def add_or_update_patient():
    if db is None:
        return jsonify({'error': 'No se puede conectar a la base de datos'}), 500

    data = request.json
    codigo = data.get('codigo')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    dni = data.get('dni')
    sexo = data.get('sexo')
    edad = data.get('edad')
    ubicacion = data.get('ubicacion')

    cursor = db.cursor()

    # Comprobar si el paciente ya existe
    cursor.execute("SELECT COUNT(*) FROM admisiones WHERE codigo = %s", (codigo,))
    exists = cursor.fetchone()[0] > 0

    if exists:
        # Actualizar el paciente existente
        cursor.execute("""
            UPDATE admisiones SET nombre = %s, apellido = %s, dni = %s, sexo = %s, edad = %s, ubicacion = %s
            WHERE codigo = %s
        """, (nombre, apellido, dni, sexo, edad, ubicacion, codigo))
    else:
        # Agregar un nuevo paciente
        cursor.execute("""
            INSERT INTO admisiones (nombre, apellido, dni, sexo, edad, codigo, ubicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, apellido, dni, sexo, edad, codigo, ubicacion))

    db.commit()
    cursor.close()
    return jsonify({'message': 'Paciente agregado o actualizado correctamente'}), 200

if __name__ == '__main__':
    app.run(port=8080, debug=True)

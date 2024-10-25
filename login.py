from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import os

# Crear una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir solicitudes CORS desde cualquier origen

# Configuración de la base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'password'),
    'database': os.getenv('DB_NAME', 'gestion')
}

# Ruta de inicio
@app.route('/')
def home():
    return render_template('1.login.html')

# Función para verificar usuario en la base de datos
def verificar_usuario(username, password):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Consulta para verificar el usuario y obtener el rol
    query = "SELECT username, password, role FROM usuarios WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return user

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verificar usuario y rol en la base de datos
    user = verificar_usuario(username, password)

    if user:
        # Puedes manejar la lógica específica para cada rol aquí si es necesario
        return jsonify(access_token='dummy_token', role=user['role']), 200
    else:
        return jsonify(message='Credenciales incorrectas'), 401

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=8080)

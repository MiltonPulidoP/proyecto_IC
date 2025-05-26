from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db import crear_base_de_datos, get_db_connection, validar_usuario, agregar_usuario

# Configuración inicial de la aplicación
app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = 'odonto'  # Clave secreta para sesiones (deberías usar una clave real en producción)

# Verificación e inicialización de la base de datos al iniciar
print("\n" + "="*50)
print("🚀 Iniciando aplicación OdontoSmile")
print("="*50 + "\n")

# Forzar la creación de la base de datos al inicio
try:
    crear_base_de_datos()
    print("✅ Base de datos verificada y lista para usar\n")
except Exception as e:
    print(f"❌ Error crítico al inicializar la base de datos: {str(e)}")
    raise

# Rutas de la aplicación
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        try:
            user = validar_usuario(email, password)
            if not user:
                flash('Correo electrónico o contraseña incorrectos', 'error')
                return redirect(url_for('login'))

            # Configurar sesión
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_role'] = user['rol']
            
            if remember:
                session.permanent = True
            
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('appointment'))

        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            data = {
                'nombres': request.form.get('nombres'),
                'apellidos': request.form.get('apellidos'),
                'telefono': request.form.get('telefono'),
                'email': request.form.get('email'),
                'rol': request.form.get('rol'),
                'password': request.form.get('password'),
                'confirm_password': request.form.get('confirm-password'),
                'age_verification': request.form.get('age-verification')
            }

            # Validaciones
            if not all(data.values()):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('register'))
                
            if data['password'] != data['confirm_password']:
                flash('Las contraseñas no coinciden', 'error')
                return redirect(url_for('register'))
                
            if len(data['password']) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return redirect(url_for('register'))
                
            if not data['age_verification']:
                flash('Debes aceptar que eres mayor de 18 años', 'error')
                return redirect(url_for('register'))

            # Registrar usuario
            agregar_usuario(
                data['nombres'],
                data['apellidos'],
                data['telefono'],
                data['email'],
                data['rol'],
                data['password']
            )
            
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'Error al registrar: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/appointment')
def appointment():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder', 'error')
        return redirect(url_for('login'))
    return render_template('appointment.html')

@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        data = request.form
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO citas (
                user_id, nombres, apellidos, email, telefono,
                tratamiento, sede, fecha, hora, tipo_paciente, edad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data['nombres'],
            data['apellidos'],
            data['email'],
            data['telefono'],
            data['tratamiento'],
            data['sede'],
            data['fecha'],
            data['hora'],
            data['tipo-paciente'],
            data['edad']
        ))
        conn.commit()
        conn.close()
        
        flash('Cita agendada exitosamente', 'success')
        return redirect(url_for('appointment'))
    
    except Exception as e:
        flash(f'Error al agendar cita: {str(e)}', 'error')
        return redirect(url_for('appointment'))

@app.route('/obtener_citas')
def obtener_citas():
    if 'user_id' not in session:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        citas = conn.execute('''
            SELECT * FROM citas 
            WHERE user_id = ?
            ORDER BY fecha, hora
        ''', (session['user_id'],)).fetchall()
        
        citas_list = [dict(cita) for cita in citas]
        return jsonify(citas_list)
        
    except Exception as e:
        print(f"Error al obtener citas: {str(e)}")
        return jsonify([])
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    # Configuración adicional para desarrollo
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, host='0.0.0.0', port=5000)
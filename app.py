import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sheets_service import SheetsService
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

db = SQLAlchemy()

class BreakState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.String(10), nullable=True)
    start_time_str = db.Column(db.String(8), nullable=True)
    is_active = db.Column(db.Boolean, default=False)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///breaks.db'
db.init_app(app)

with app.app_context():
    db.create_all()
    # Reset any active break state on startup
    break_state = BreakState.query.first()
    if break_state:
        break_state.is_active = False
        db.session.commit()

# Initialize Google Sheets service
sheets_service = None
try:
    sheets_service = SheetsService()
    logger.info("Servicio de Google Sheets inicializado correctamente.")
except Exception as e:
    logger.error(f"Fallo al cargar los servicios de Google Sheets: {str(e)}")

@app.route('/health')
def health():
    logger.info("Punto de Salud accedido")
    return "OK", 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-break', methods=['POST'])
def start_break():
    try:
        if not sheets_service:
            return jsonify({
                'status': 'error',
                'message': 'Servicios de Google Sheets no disponibles'
            }), 500

        current_time = datetime.now()
        date_str = current_time.strftime('%d/%m/%Y')
        time_str = current_time.strftime('%H:%M:%S')

        # Store break state in database
        break_state = BreakState.query.first()
        if not break_state:
            break_state = BreakState()
            db.session.add(break_state)
        
        break_state.start_time = current_time
        break_state.start_date = date_str
        break_state.start_time_str = time_str
        break_state.is_active = True
        db.session.commit()

        return jsonify({
            'status': 'success',
            'date': date_str,
            'time': time_str
        })
    except Exception as e:
        logger.error(f"Error empezando el descanso: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/check-break-status', methods=['GET'])
def check_break_status():
    break_state = BreakState.query.first()
    if break_state and break_state.is_active:
        return jsonify({
            'status': 'active',
            'start_date': break_state.start_date,
            'start_time': break_state.start_time_str,
            'start_timestamp': break_state.start_time.timestamp()
        })
    return jsonify({'status': 'inactive'})

@app.route('/end-break', methods=['POST'])
def end_break():
    try:
        if not sheets_service:
            return jsonify({
                'status': 'error',
                'message': 'Servicio de Google Sheets no configurado correctamente'
            }), 500

        break_state = BreakState.query.first()
        if not break_state or not break_state.is_active:
            return jsonify({
                'status': 'error',
                'message': 'No hay descanso activo'
            }), 400

        current_time = datetime.now()
        end_time = current_time.strftime('%H:%M:%S')
        reason = request.json.get('reason', '').strip()

        if not reason:
            return jsonify({
                'status': 'error',
                'message': 'Razón de descanso requerida'
            }), 400

        # Log to Google Sheets
        try:
            sheets_service.log_break(
                date=break_state.start_date,
                start_time=break_state.start_time_str,
                end_time=end_time,
                reason=reason
            )
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

        # Clear the stored start time
        app.config.pop('break_start', None)

        return jsonify({
            'status': 'success',
            'message': 'Registro de descanso guardado correctamente'
        })
    except Exception as e:
        logger.error(f"Error ending break: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Un error ocurrió al finalizar el descanso'
        }), 500

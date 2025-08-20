from datetime import datetime
from apps.database.database import get_db
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from apps.controller.LoginController import LoginController
from apps.controller.SignUpController import SignUpController
from apps.controller.InputController import InputController
from apps.controller.PreprocessingController import PreprocessingController
from apps.controller.AprioriController import AprioriController
from apps.controller.FPGrowthController import FPGrowthController
from apps.controller.ResultController import ResultController

bp = Blueprint('routes', __name__)

@bp.route("/", methods=["GET"])
def landing():  
    return render_template('pages/landing.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return LoginController.login_post()
    return LoginController.login_index()

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return SignUpController.signup_post()
    return SignUpController.signup_index()

@bp.route("/dashboard", methods=["GET"])
def dashboard():
    # Check user authentication
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')
        return redirect(url_for('routes.login'))
    
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get file info (menggunakan tuple index)
        cursor.execute('SELECT * FROM file_infos LIMIT 1')
        file_info = cursor.fetchone()
        
        # Get all transaction items
        cursor.execute('SELECT item FROM data_transactions')
        items_data = cursor.fetchall()
        
        # Get accuracy values from both metrics
        cursor.execute('SELECT avg_accuracy FROM metrics_ap LIMIT 1')
        metrics_ap = cursor.fetchone()
        
        cursor.execute('SELECT avg_accuracy FROM metrics_fp LIMIT 1')
        metrics_fp = cursor.fetchone()
        
        # Handle null values by defaulting to 0 (menggunakan tuple index)
        accuracy_ap = metrics_ap[0] if metrics_ap and metrics_ap[0] is not None else 0
        accuracy_fp = metrics_fp[0] if metrics_fp and metrics_fp[0] is not None else 0
        
        # Determine which algorithm performed better
        best_algorithms = []
        if accuracy_ap > accuracy_fp:
            best_algorithms.append({'name': 'Apriori', 'accuracy': accuracy_ap})
        elif accuracy_fp > accuracy_ap:
            best_algorithms.append({'name': 'FP-Growth', 'accuracy': accuracy_fp})
        else:
            best_algorithms.append({'name': 'Apriori', 'accuracy': accuracy_ap})
            best_algorithms.append({'name': 'FP-Growth', 'accuracy': accuracy_fp})
        
        # Process item frequency data
        item_counts = {}
        for row in items_data:
            # row[0] karena kita hanya select item (tuple index)
            if row[0]:  # Check if item is not None
                items = [item.strip() for item in row[0].split(',') if item.strip()]
                for item in items:
                    item_counts[item] = item_counts.get(item, 0) + 1
        
        # Get top 5 items by frequency
        top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return render_template(
            'pages/dashboard.html', 
            header_title='Dashboard', 
            file_info=file_info,
            top_items=top_items,
            best_algorithms=best_algorithms,
            accuracy_ap=accuracy_ap,
            accuracy_fp=accuracy_fp
        )
        
    except Exception as e:
        flash(f'Terjadi kesalahan saat memuat dashboard: {str(e)}', 'error')
        return redirect(url_for('routes.dashboard'))
    finally:
        if cursor:
            cursor.close()


@bp.route("/input", methods=["GET", "POST"])
def input():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    if request.method == 'POST':
        return InputController.input_post()
    # Pesan jika sudah login
    # flash('Anda sudah login', 'success')
    return InputController.input_index()

@bp.route("/preprocessing", methods=["GET", "POST"])
def preprocessing():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return PreprocessingController.preprocessing_index()

@bp.route("/process", methods=["POST"])
def process():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return PreprocessingController.process_index()

@bp.route("/preprocessing-split", methods=["GET"])
def preprocessing_split():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return PreprocessingController.preprocessing_split()

@bp.route("/preprocessing-basket", methods=["GET"])
def preprocessing_basket():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return PreprocessingController.preprocessing_basket()

@bp.route("/preprocessing-onehot", methods=["GET"])
def preprocessing_onehot():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return PreprocessingController.preprocessing_onehot()

@bp.route("/apriori", methods=["GET"])
def apriori():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return AprioriController.apriori_index()

@bp.route("/calculate-apriori", methods=["GET"])
def calculate_apriori():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return AprioriController.calculate_apriori()

@bp.route("/setup-apriori", methods=["POST"])
def setup():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return AprioriController.setup_ap()

@bp.route("/process-apriori", methods=["POST"])
def process_apriori():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return AprioriController.process_index()


@bp.route("/fp-growth", methods=["GET"])
def fpgrowth():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return FPGrowthController.fpgrowth_index()

@bp.route("/setup-fpgrowth", methods=["POST"])
def setupfp():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return FPGrowthController.setup_fp()

@bp.route("/process-fpgrowth", methods=["POST"])
def process_fpgrowth():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return FPGrowthController.process_index()


@bp.route("/result", methods=["GET"])
def result():  
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')  # Pesan jika belum login
        return redirect(url_for('routes.login'))
    
    return ResultController.result_index()

@bp.route('/logout')
def logout():
    session.clear()  
    flash('Berhasil logout.', 'success')
    return redirect(url_for('routes.login'))
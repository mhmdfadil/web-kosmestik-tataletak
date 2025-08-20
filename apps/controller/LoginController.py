# LoginController.py
import hashlib
from flask import flash, request, url_for, session, redirect, render_template
from apps.database.database import get_db 

class LoginController:
    @staticmethod
    def login_index():
        return render_template('auth/login.html')

    @staticmethod
    def login_post():
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()

            if not email or not password:
                flash('Email dan password wajib diisi.', 'info')
                return redirect(url_for('routes.login'))
            
            if '@' not in email or '.' not in email or email.count('@') != 1:
                flash('Email tidak valid.', 'info')
                return redirect(url_for('routes.login'))

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Using tuple indexing instead of dictionary
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'SELECT id, email, password FROM users WHERE email = %s',
                (email,)
            )
            user = cursor.fetchone()
            cursor.close()

            if not user:
                flash('Email tidak ditemukan.', 'error')
                return redirect(url_for('routes.login'))
                
            if user[2] != hashed_password:  # password is at index 2
                flash('Password salah.', 'error')
                return redirect(url_for('routes.login'))

            session['user_id'] = user[0]  
            flash('Berhasil login.', 'success')
            return redirect(url_for('routes.dashboard'))
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            flash('Terjadi kesalahan saat proses login.', 'error')
            return redirect(url_for('routes.login'))
import hashlib
from flask import Flask, flash, request, jsonify, url_for, session, render_template, redirect
from apps.database.database import get_db
from functools import wraps

class SignUpController:
    @staticmethod
    def signup_index():
        return render_template('auth/register.html')
    
    @staticmethod
    def signup_post():
        # Ambil data dari form
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        cpassword = request.form.get('confirm-password', '').strip()
        
        # Validasi input wajib diisi
        if not email or not password or not cpassword:
            flash('Semua data form wajib diisi.', 'info')
            return redirect(url_for('routes.signup'))
            
        # Validasi format email lebih baik
        if '@' not in email or '.' not in email or email.count('@') != 1:
            flash('Email tidak valid.', 'info')
            return redirect(url_for('routes.signup'))
            
        # Validasi panjang password
        if len(password) < 8:
            flash('Password minimal 8 karakter.', 'info')
            return redirect(url_for('routes.signup'))
            
        # Validasi kesesuaian password
        if password != cpassword:
            flash('Password dan konfirmasi password tidak sama.', 'info')
            return redirect(url_for('routes.signup'))
            
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Gunakan parameterized query dengan placeholder yang benar (%s untuk MySQL)
            cursor.execute(
                'SELECT id, email, password FROM users WHERE email = %s',
                (email,)
            )
            user = cursor.fetchone()
            
            if user:
                flash('Email sudah terdaftar.', 'error')
                return redirect(url_for('routes.signup'))
                
            # Hash password dengan lebih secure method (consider using bcrypt instead)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Simpan user baru
            cursor.execute(
                'INSERT INTO users (email, password) VALUES (%s, %s)',
                (email, hashed_password)
            )
            db.commit()
            
            flash('Berhasil sign up.', 'success')
            return redirect(url_for('routes.login'))  # Ganti dengan route tujuan setelah signup
            
        except Exception as e:
            db.rollback()
            flash('Terjadi kesalahan saat mendaftar.', 'error')
            return redirect(url_for('routes.signup'))
        finally:
            cursor.close()
import hashlib
import os
from flask import Flask, flash, request, jsonify, url_for, session, render_template, redirect
from apps.database.database import get_db
from functools import wraps
from datetime import datetime
import pandas as pd
import openpyxl
import csv
from io import StringIO
from werkzeug.utils import secure_filename

class ProfileController:
    @staticmethod
    def profile_index():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            
            return render_template(
                'pages/profile.html', 
                header_title='Profile Saya',
                user=user
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('routes.profile'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def profile_post():
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Ambil data user saat ini
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            current_user = cursor.fetchone()
            
            # Jika menggunakan tuple, kita perlu tahu urutan kolom
            # Asumsi urutan kolom: id, fullname, email, phone, gender, password, photos, ...
            user_id_idx = 0
            fullname_idx = 3
            email_idx = 1
            phone_idx = 5
            gender_idx = 4
            password_idx = 2
            photos_idx = 6
            
            # Ambil data dari form
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            gender = request.form.get('gender')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validasi email unik (kecuali untuk user yang sedang login)
            if email != current_user[email_idx]:
                cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, session['user_id']))
                if cursor.fetchone():
                    flash('Email sudah digunakan oleh pengguna lain', 'danger')
                    return redirect(url_for('routes.profile'))
            
            # Inisialisasi variabel untuk query update
            update_fields = []
            params = []
            
            # Update field yang diisi
            if fullname and fullname != current_user[fullname_idx]:
                update_fields.append("fullname = %s")
                params.append(fullname)
            
            if email and email != current_user[email_idx]:
                update_fields.append("email = %s")
                params.append(email)
            
            if phone != current_user[phone_idx]:  # Phone bisa kosong
                update_fields.append("phone = %s")
                params.append(phone)
            
            if gender != current_user[gender_idx]:  # Gender bisa kosong
                update_fields.append("gender = %s")
                params.append(gender)
            
            # Validasi password jika diisi
            if new_password:
                if len(new_password) < 8:
                    flash('Password harus minimal 8 karakter', 'danger')
                    return redirect(url_for('routes.profile'))
                
                if new_password != confirm_password:
                    flash('Konfirmasi password tidak sesuai', 'danger')
                    return redirect(url_for('routes.profile'))
                
                # Hash password dengan SHA256
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                update_fields.append("password = %s")
                params.append(hashed_password)
            
            # Handle file upload
            if 'photos' in request.files:
                file = request.files['photos']
                if file and file.filename:
                    # Pastikan direktori ada
                    upload_dir = os.path.join('apps', 'static', 'images')
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    
                    # Generate nama file yang aman
                    filename = secure_filename(file.filename)
                    # Tambahkan timestamp untuk menghindari konflik nama file
                    filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Hapus foto lama jika ada dan bukan default
                    if current_user[photos_idx] and current_user[photos_idx] != 'default-avatar.png':
                        old_file_path = os.path.join(upload_dir, current_user[photos_idx])
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    update_fields.append("photos = %s")
                    params.append(filename)
            
            # Jika tidak ada yang diupdate
            if not update_fields:
                flash('Tidak ada perubahan data', 'info')
                return redirect(url_for('routes.profile'))
            
            # Tambahkan user_id ke parameter
            params.append(session['user_id'])
            
            # Bangun query update
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            
            # Eksekusi query
            cursor.execute(query, tuple(params))
            db.commit()
            
            flash('Profil berhasil diperbarui', 'success')
            return redirect(url_for('routes.profile'))
            
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            return redirect(url_for('routes.profile'))
        finally:
            if cursor:
                cursor.close()
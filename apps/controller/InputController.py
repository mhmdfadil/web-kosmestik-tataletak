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

class InputController:
    @staticmethod
    def input_index():
        # Check user authentication
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'info')
            return redirect(url_for('routes.login'))
        
        db = get_db()
        cursor = None
        try:
            cursor = db.cursor()  # dictionary=True biar hasilnya dict
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                flash("User tidak ditemukan.", "error")
                return redirect(url_for('routes.login'))
            
            return render_template('pages/input.html', header_title='Input Transaksi', user=user)
        
        except Exception as e:
            flash(f'Terjadi kesalahan saat memuat dashboard: {str(e)}', 'error')
            return redirect(url_for('routes.input'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def input_post():
        ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
        REQUIRED_COLUMNS = ['ID Transaksi', 'Tahun', 'Item']
        
        # Validasi unggahan file
        if 'file' not in request.files:
            flash('Tidak ada file yang diunggah', 'error')
            return redirect(url_for('routes.input'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih', 'error')
            return redirect(url_for('routes.input'))
        
        # Validasi ekstensi file
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            flash('Jenis file tidak valid. Hanya file CSV dan Excel yang diperbolehkan.', 'error')
            return redirect(url_for('routes.input'))
        
        db = None
        cursor = None
        try:
            # Membaca file berdasarkan ekstensi
            if file_ext == '.csv':
                try:
                    # Membaca file CSV dengan encoding eksplisit
                    stream = StringIO(file.stream.read().decode("UTF-8"), newline=None)
                    df = pd.read_csv(stream)
                except UnicodeDecodeError:
                    # Coba encoding alternatif jika UTF-8 gagal
                    stream = StringIO(file.stream.read().decode("ISO-8859-1"), newline=None)
                    df = pd.read_csv(stream)
            else:
                # Membaca file Excel
                df = pd.read_excel(file)
            
            # Memeriksa kolom yang diperlukan
            missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                flash(f'Kolom wajib tidak ditemukan: {", ".join(missing_columns)}', 'error')
                return redirect(url_for('routes.input'))
            
            # Membersihkan data
            df = df.dropna(subset=REQUIRED_COLUMNS)
            df = df[df['ID Transaksi'].str.startswith('T', na=False)]  # Handle nilai NaN
            
            if df.empty:
                flash('Tidak ada data yang valid setelah pembersihan', 'error')
                return redirect(url_for('routes.input'))
            
            # Menghitung info file
            count_transaction = len(df)
            
            # Mengolah tahun dengan benar
            years = df['Tahun'].dropna().unique()
            
            # Konversi tahun ke integer untuk pengurutan yang benar
            try:
                years_int = sorted([int(year) for year in years])
                if len(years_int) == 1:
                    year_range = str(years_int[0])
                else:
                    year_range = f"{min(years_int)} - {max(years_int)}"
            except (ValueError, TypeError):
                # Jika konversi gagal, gunakan nilai asli
                years_sorted = sorted(years)
                if len(years_sorted) == 1:
                    year_range = str(years_sorted[0])
                else:
                    year_range = f"{years_sorted[0]} - {years_sorted[-1]}"
            
            # Menghitung jumlah item unik dengan lebih efisien
            all_items = set()
            for items in df['Item']:
                items_list = {item.strip() for item in str(items).split(',') if item.strip()}
                all_items.update(items_list)
            
            count_item = len(all_items)
            
            db = get_db()
            cursor = db.cursor()
            
            # Memulai transaksi
            cursor.execute('BEGIN')
            
            # Menghapus data yang ada terlebih dahulu
            cursor.execute('DELETE FROM data_transactions')
            cursor.execute('DELETE FROM file_infos')
            # Membersihkan hasil sebelumnya
            cursor.execute('DELETE FROM frequent_ap')
            cursor.execute('DELETE FROM detail_frequent_ap')
            cursor.execute('DELETE FROM association_rule_ap')
            cursor.execute('DELETE FROM metrics_ap')
            # Membersihkan hasil sebelumnya
            cursor.execute('DELETE FROM frequent_fp')
            cursor.execute('DELETE FROM detail_frequent_fp')
            cursor.execute('DELETE FROM association_rule_fp')
            cursor.execute('DELETE FROM item_initial_fp')
            cursor.execute('DELETE FROM transaction_process_fp')
            cursor.execute('DELETE FROM mining_fptree_fp')
            cursor.execute('DELETE FROM metrics_fp')
            
            # Mereset flag proses
            cursor.execute('''
                UPDATE process 
                SET preprocessing = %s, apriori = %s, fp_growth = %s, updated_at = %s
                WHERE id = (SELECT id FROM process LIMIT 1)
            ''', (False, False, False, datetime.now()))
            
            # Memasukkan info file
            cursor.execute('''
                INSERT INTO file_infos 
                (filename, count_transaction, count_item, year) 
                VALUES (%s, %s, %s, %s)
            ''', (file.filename, count_transaction, count_item, year_range))
            
            file_id = cursor.lastrowid
            
            # Memasukkan transaksi menggunakan executemany untuk performa lebih baik
            transactions_data = [
                (file_id, row['ID Transaksi'], row['Tahun'], row['Item'])
                for _, row in df.iterrows()
            ]
            
            cursor.executemany('''
                INSERT INTO data_transactions 
                (file_id, code_transaction, year, item) 
                VALUES (%s, %s, %s, %s)
            ''', transactions_data)
            
            db.commit()
            flash('Data berhasil diunggah dan diproses!', 'success')
            return redirect(url_for('routes.input'))
            
        except pd.errors.EmptyDataError:
            flash('File yang diunggah kosong', 'error')
            return redirect(url_for('routes.input'))
        except pd.errors.ParserError:
            flash('Gagal memproses file. Silakan periksa format file.', 'error')
            return redirect(url_for('routes.input'))
        except Exception as e:
            if db:
                db.rollback()
            flash(f'Gagal memproses file: {str(e)}', 'error')
            return redirect(url_for('routes.input'))
        finally:
            if cursor:
                cursor.close()
            if db:
                cursor.close()
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

class PreprocessingController:
    @staticmethod
    def preprocessing_index():
        try:
            db = get_db()
            cursor = db.cursor()
            # Mengambil hanya 1 data pertama dari tabel file_infos
            cursor.execute('SELECT * FROM file_infos LIMIT 1')
            file_info = cursor.fetchone()
            
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            return render_template(
                'pages/preprocessing.html', 
                header_title='Pemrosesan Data',
                process=process,
                file_info=file_info  # Mengirim 1 data file_info ke template
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.dashboard'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def process_index():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            if process is not None:
                cursor.execute(
                    'UPDATE process SET preprocessing = %s, updated_at = %s WHERE id = %s', 
                    (True, datetime.now(), process[0])
                )
                db.commit()
                flash('Berhasil diproses. Anda memiliki izin melihat tahapan pemrosesan data.', 'success')
            
            return redirect(url_for('routes.preprocessing'))
        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.preprocessing'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def preprocessing_split():
        try:
            db = get_db()
            cursor = db.cursor()
            # Get all transactions ordered by year
            cursor.execute('SELECT code_transaction, year, item FROM data_transactions ORDER BY id')
            transactions = cursor.fetchall()
            
            # Find the maximum number of items in any transaction
            max_items = 0
            for transaction in transactions:
                items = transaction[2].split(', ')
                if len(items) > max_items:
                    max_items = len(items)
            
            return render_template(
                'pages/preprocessing_split.html', 
                header_title='Pemrosesan: Split Data',
                transactions=transactions,
                max_items=max_items
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.preprocessing'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def preprocessing_basket():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT item FROM data_transactions')
            data_transaction = cursor.fetchall()
            
            # Process the data into the desired array format
            basket_data = []
            for transaction in data_transaction:
                items = transaction[0].split(', ')
                basket_data.append(items)
            
            return render_template(
                'pages/preprocessing_basket.html', 
                header_title='Pemrosesan: Basket Data',
                data_transaction=data_transaction,
                basket_data=basket_data
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.preprocessing'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def preprocessing_onehot():
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get all transactions
            cursor.execute('SELECT code_transaction, item FROM data_transactions')
            transactions = cursor.fetchall()
            
            # Get all unique items
            all_items = set()
            for transaction in transactions:
                items = transaction[1].split(', ')
                all_items.update(items)
            
            # Convert to sorted list
            unique_items = sorted(list(all_items))
            
            # Prepare one-hot encoded data
            onehot_data = []
            for transaction in transactions:
                transaction_items = transaction[1].split(', ')
                encoded = [1 if item in transaction_items else 0 for item in unique_items]
                onehot_data.append(encoded)
            
            return render_template(
                'pages/preprocessing_onehot.html', 
                header_title='Pemrosesan: One Hot Data',
                unique_items=unique_items,
                transactions=transactions,
                onehot_data=onehot_data
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.preprocessing'))
        finally:
            if cursor:
                cursor.close()
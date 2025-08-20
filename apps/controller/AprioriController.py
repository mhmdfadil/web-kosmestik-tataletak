import hashlib
import os
import time
import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict
from flask import Flask, flash, request, jsonify, url_for, session, render_template, redirect
from apps.database.database import get_db
from functools import wraps
from datetime import datetime

class AprioriController:

    @staticmethod
    def process_index():
        try:
            db = get_db()
            cursor = db.cursor()
            
            
            # Get process status
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            # Get setup parameters
            cursor.execute('SELECT min_support_ap, min_confidance_ap FROM setups LIMIT 1')
            setup = cursor.fetchone()
            if not setup:
                flash('Parameter setup belum diisi', 'error')
                return redirect(url_for('routes.apriori'))
                
            min_support = setup[0]
            min_confidence = setup[1]

            # Get all transactions with one-hot encoded format
            cursor.execute('''
                SELECT dt.id, dt.item, fi.year 
                FROM data_transactions dt 
                JOIN file_infos fi ON dt.file_id = fi.id
            ''')
            transactions_data = cursor.fetchall()
            
            if not transactions_data:
                flash('Tidak ada data transaksi', 'error')
                return redirect(url_for('routes.apriori'))
            
            # Create transaction list and extract unique items
            transactions = []
            transaction_ids = []
            years = []
            all_items = set()
            
            for row in transactions_data:
                transaction_ids.append(row[0])
                items = row[1].split(', ')
                transactions.append(items)
                all_items.update(items)
                years.append(row[2])
            
            total_transactions = len(transactions)
            
            # Create one-hot encoded matrix using pandas
            item_list = sorted(list(all_items))
            df = pd.DataFrame(0, index=range(total_transactions), columns=item_list)

            start_time = time.time()
            
            for i, transaction in enumerate(transactions):
                for item in transaction:
                    if item in df.columns:
                        df.loc[i, item] = 1
            
            # Add ID and Year columns
            df['ID Transaksi'] = transaction_ids
            df['Tahun'] = years
            
            # Convert to numpy array for efficient computation
            item_columns = [col for col in df.columns if col not in ['ID Transaksi', 'Tahun']]
            transaction_matrix = df[item_columns].values.astype(bool)
            
            # Create mapping between item names and indices
            item_to_idx = {item: idx for idx, item in enumerate(item_columns)}
            idx_to_item = {idx: item for idx, item in enumerate(item_columns)}
            
            # Function to calculate support using numpy for efficiency
            def calculate_support_numpy(itemset_indices):
                if len(itemset_indices) == 1:
                    support_count = np.sum(transaction_matrix[:, itemset_indices[0]])
                else:
                    support_count = np.sum(np.all(transaction_matrix[:, itemset_indices], axis=1))
                return support_count, support_count / total_transactions
            
            

            # Step 1: Find frequent 1-itemsets
            frequent_itemsets = {}
            frequent_results = {}
            k = 1
            frequent_itemsets[k] = {}
            frequent_results[k] = []
            
            # Store all 1-itemsets in database
            cursor.execute('INSERT INTO frequent_ap (name) VALUES (%s)', ('Frequent 1-itemset',))
            frequent_id = cursor.lastrowid
            
            for item in item_columns:
                idx = item_to_idx[item]
                support_count, support = calculate_support_numpy([idx])
                status = "Lolos" if support >= min_support else "Tidak Lolos"
                
                frequent_results[k].append({
                    'item': item,
                    'transaction_count': support_count,
                    'support': support,
                    'status': status
                })
                
                # Store in database
                cursor.execute(
                    '''INSERT INTO detail_frequent_ap 
                    (item, transaction_count, support, description, frequent_id) 
                    VALUES (%s, %s, %s, %s, %s)''',
                    (item, support_count, round(support, 4), status, frequent_id)
                )
                
                if support >= min_support:
                    frequent_itemsets[k][frozenset([item])] = support
            
            db.commit()
            
            # Step 2: Iterate to find larger itemsets
            k = 2
            while True:
                frequent_itemsets[k] = {}
                frequent_results[k] = []
                
                # Generate candidate itemsets from previous frequent itemsets
                candidates = set()
                prev_itemsets = list(frequent_itemsets[k-1].keys())
                
                # Generate candidates by joining frequent (k-1)-itemsets
                for i in range(len(prev_itemsets)):
                    for j in range(i + 1, len(prev_itemsets)):
                        itemset1 = prev_itemsets[i]
                        itemset2 = prev_itemsets[j]
                        union_set = itemset1 | itemset2
                        if len(union_set) == k:
                            candidates.add(frozenset(union_set))
                
                candidates = list(candidates)
                
                # Store all k-itemsets in database
                cursor.execute('INSERT INTO frequent_ap (name) VALUES (%s)', (f'Frequent {k}-itemset',))
                frequent_id = cursor.lastrowid
                
                for candidate in candidates:
                    # Prune step: Check if all subsets are frequent
                    all_subsets_frequent = True
                    for subset in combinations(candidate, k-1):
                        if frozenset(subset) not in frequent_itemsets[k-1]:
                            all_subsets_frequent = False
                            break
                    
                    if all_subsets_frequent:
                        candidate_indices = [item_to_idx[item] for item in candidate]
                        support_count, support = calculate_support_numpy(candidate_indices)
                        status = "Lolos" if support >= min_support else "Tidak Lolos"
                        
                        itemset_str = ', '.join(candidate)
                        frequent_results[k].append({
                            'item': itemset_str,
                            'transaction_count': support_count,
                            'support': support,
                            'status': status
                        })
                        
                        # Store in database
                        cursor.execute(
                            '''INSERT INTO detail_frequent_ap 
                            (item, transaction_count, support, description, frequent_id) 
                            VALUES (%s, %s, %s, %s, %s)''',
                            (itemset_str, support_count, round(support, 4), status, frequent_id)
                        )
                        
                        if support >= min_support:
                            frequent_itemsets[k][candidate] = support
                
                db.commit()
                
                # Stop if no frequent itemsets found at this level
                if not frequent_itemsets[k]:
                    del frequent_itemsets[k]
                    del frequent_results[k]
                    break
                
                k += 1
            
            # Step 3: Generate association rules from frequent itemsets
            association_rules = []
            
            # Process itemsets of size 2 or larger
            for k, itemsets in list(frequent_itemsets.items())[1:]:
                for itemset in itemsets.keys():
                    # Generate all possible non-empty subsets
                    for i in range(1, len(itemset)):
                        for antecedent in combinations(itemset, i):
                            antecedent = frozenset(antecedent)
                            consequent = itemset - antecedent
                            
                            # Get support values
                            support_A = frequent_itemsets[len(antecedent)][antecedent]
                            support_B = frequent_itemsets[len(consequent)][consequent]
                            support_AUB = frequent_itemsets[len(itemset)][itemset]
                            
                            # Calculate confidence
                            confidence = support_AUB / support_A
                            
                            # Only keep rules meeting minimum confidence
                            if confidence >= min_confidence:
                                # Calculate lift
                                lift = confidence / support_B
                                
                                # Determine correlation type
                                correlation = "Positif" if lift > 1 else "Negatif" if lift < 1 else "Netral"
                                
                                # Calculate additional metrics
                                precision = confidence
                                recall = precision
                                accuracy = (precision + recall) / 2
                                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                                
                                rule_str = f"{set(antecedent)} => {set(consequent)}"
                                
                                rule_data = {
                                    'rule': rule_str,
                                    'support_A': round(support_A, 4),
                                    'support_B': round(support_B, 4),
                                    'support_AUB': round(support_AUB, 4),
                                    'confidence': round(confidence, 4),
                                    'lift': round(lift, 4),
                                    'correlation': correlation,
                                    'accuracy': round(accuracy, 4),
                                    'precision': round(precision, 4),
                                    'recall': round(recall, 4),
                                    'f1_score': round(f1_score, 4)
                                }
                                association_rules.append(rule_data)
                                
                                # Store rule in database
                                cursor.execute(
                                    '''INSERT INTO association_rule_ap 
                                    (rule, support_a, support_b, support_aub, confidence, lift, correlation, 
                                    accuracy, precision_val, recall_val, f1_score_val) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                    (
                                        rule_str, round(support_A, 4), round(support_B, 4), round(support_AUB, 4),
                                        round(confidence, 4), round(lift, 4), correlation, round(accuracy, 4),
                                        round(precision, 4), round(recall, 4), round(f1_score, 4)
                                    )
                                )
            
            db.commit()
            
            # Calculate and store metrics
            execution_time = round(time.time() - start_time, 2)
            num_rules = len(association_rules)
            avg_lift = np.mean([rule['lift'] for rule in association_rules]) if num_rules > 0 else 0
            avg_accuracy = np.mean([rule['accuracy'] for rule in association_rules]) if num_rules > 0 else 0
            
            cursor.execute(
                '''INSERT INTO metrics_ap 
                (execution_time, total_rules_found, avg_lift, avg_accuracy) 
                VALUES (%s, %s, %s, %s)''',
                (f"{execution_time} detik", num_rules, round(avg_lift, 4), round(avg_accuracy, 4))
            )
            
            # Update process status
            if process:
                cursor.execute(
                    'UPDATE process SET apriori = %s, updated_at = %s WHERE id = %s',
                    (True, datetime.now(), process[0])
                )
            
            db.commit()
            flash('Berhasil diproses perhitungan Apriori. Lihat hasil perhitungan.', 'success')
            return redirect(url_for('routes.apriori'))

        except Exception as e:
            db.rollback()
            flash(f'Terjadi kesalahan saat memproses Apriori: {str(e)}', 'error')
            return redirect(url_for('routes.apriori'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def setup_ap():
        if request.method == 'POST':
            try:
                min_support_ap = float(request.form.get('min_support_ap', 0))
                min_confidance_ap = float(request.form.get('min_confidance_ap', 0))
                
                if not 0 <= min_support_ap <= 1 or not 0 <= min_confidance_ap <= 1:
                    flash('Nilai harus antara 0 dan 1', 'error')
                    return redirect(url_for('routes.apriori'))
                
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT id FROM setups LIMIT 1')
                setup = cursor.fetchone()
                
                if setup:
                    cursor.execute(
                        '''UPDATE setups 
                        SET min_support_ap = %s, min_confidance_ap = %s, updated_at = %s 
                        WHERE id = %s''',
                        (min_support_ap, min_confidance_ap, datetime.now(), setup[0])
                    )
                else:
                    cursor.execute(
                        '''INSERT INTO setups 
                        (min_support_ap, min_confidance_ap, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s)''',
                        (min_support_ap, min_confidance_ap, datetime.now(), datetime.now())
                    )
                
                # Clear previous results
                cursor.execute('DELETE FROM frequent_ap')
                cursor.execute('DELETE FROM detail_frequent_ap')
                cursor.execute('DELETE FROM association_rule_ap')
                cursor.execute('DELETE FROM metrics_ap')
                cursor.execute(
                    '''UPDATE process 
                    SET apriori = %s, updated_at = %s
                    WHERE id = (SELECT id FROM process LIMIT 1)''',
                    (False, datetime.now())
                )
                
                db.commit()
                flash('Berhasil memperbarui nilai minimum support dan confidence', 'success')
            except ValueError:
                flash('Nilai tidak valid', 'error')
            except Exception as e:
                db.rollback()
                flash(f'Terjadi kesalahan: {str(e)}', 'error')
            finally:
                if cursor:
                    cursor.close()
            
            return redirect(url_for('routes.apriori'))
        
        return redirect(url_for('routes.apriori'))

    @staticmethod
    def calculate_apriori():
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            
            # Get setup parameters
            cursor.execute('SELECT min_support_ap, min_confidance_ap FROM setups LIMIT 1')
            setup = cursor.fetchone()
            if not setup:
                setup = {'min_support_ap': 0.3, 'min_confidance_ap': 0.6}
            
            # Get file info
            cursor.execute('SELECT * FROM file_infos LIMIT 1')
            file_info = cursor.fetchone()
            if not file_info:
                file_info = {
                    'filename': 'No file uploaded', 
                    'count_transaction': 0, 
                    'count_item': 0, 
                    'year': 'N/A'
                }
            
            # Get frequent itemsets
            cursor.execute('SELECT * FROM frequent_ap ORDER BY id')
            frequent_ap = cursor.fetchall()
            
            cursor.execute('''
                SELECT df.*, f.name as frequent_name 
                FROM detail_frequent_ap df 
                JOIN frequent_ap f ON df.frequent_id = f.id 
                ORDER BY f.id, df.id
            ''')
            detail_frequent_ap = cursor.fetchall()
            
            # Get association rules
            cursor.execute('SELECT * FROM association_rule_ap ORDER BY id')
            association_rule = cursor.fetchall()
            
            # Get metrics
            cursor.execute('SELECT * FROM metrics_ap ORDER BY id DESC LIMIT 1')
            metric = cursor.fetchone()
            if not metric:
                metric = {
                    'execution_time': 'N/A', 
                    'total_rules_found': 0, 
                    'avg_lift': 0, 
                    'avg_accuracy': 0
                }
            
            return render_template(
                'pages/calculate_apriori.html',
                header_title='Perhitungan Apriori',
                user=user,
                frequent_ap=frequent_ap,
                detail_frequent_ap=detail_frequent_ap,
                association_rule=association_rule,
                metric=metric,
                file_info=file_info,
                setup=setup
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.apriori'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def apriori_index():
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()

            cursor.execute('SELECT * FROM file_infos LIMIT 1')
            file_info = cursor.fetchone()
            
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            cursor.execute('SELECT * FROM setups LIMIT 1')
            setup = cursor.fetchone()
            
            return render_template(
                'pages/apriori.html', 
                header_title='Algoritma Apriori', 
                user=user,
                process=process, 
                file_info=file_info, 
                setup=setup
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.apriori'))
        finally:
            if cursor:
                cursor.close()
import hashlib
import os
import time
from itertools import combinations
from collections import defaultdict
from flask import Flask, flash, request, jsonify, url_for, session, render_template, redirect
from apps.database.database import get_db
from functools import wraps
from datetime import datetime

class FPGrowthController:
    @staticmethod
    def fpgrowth_index():
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get file info
            cursor.execute('SELECT * FROM file_infos LIMIT 1')
            file_info = cursor.fetchone()
            
            # Get process status
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            # Get setup parameters
            cursor.execute('SELECT * FROM setups LIMIT 1')
            setup = cursor.fetchone()
            
            return render_template(
                'pages/fp_growth.html', 
                header_title='Algoritma FP-Growth', 
                process=process, 
                file_info=file_info, 
                setup=setup
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.dashboard'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def setup_fp():
        if request.method == 'POST':
            cursor = None
            try:
                # Get and validate form data
                min_support_fp = float(request.form.get('min_support_fp', 0))
                min_confidance_fp = float(request.form.get('min_confidance_fp', 0))
                
                if not 0 <= min_support_fp <= 1 or not 0 <= min_confidance_fp <= 1:
                    flash('Nilai harus antara 0 dan 1', 'error')
                    return redirect(url_for('routes.fpgrowth'))
                
                db = get_db()
                cursor = db.cursor()
                
                # Check if setup exists
                cursor.execute('SELECT id FROM setups LIMIT 1')
                setup = cursor.fetchone()
                
                if setup:
                    # Update existing setup
                    cursor.execute(
                        '''UPDATE setups 
                        SET min_support_fp = %s, min_confidance_fp = %s, updated_at = %s 
                        WHERE id = %s''',
                        (min_support_fp, min_confidance_fp, datetime.now(), setup[0])
                    )
                else:
                    # Insert new setup
                    cursor.execute(
                        '''INSERT INTO setups 
                        (min_support_fp, min_confidance_fp, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s)''',
                        (min_support_fp, min_confidance_fp, datetime.now(), datetime.now())
                    )
                
                # Clear previous results
                cursor.execute('DELETE FROM frequent_fp')
                cursor.execute('DELETE FROM detail_frequent_fp')
                cursor.execute('DELETE FROM association_rule_fp')
                cursor.execute('DELETE FROM item_initial_fp')
                cursor.execute('DELETE FROM transaction_process_fp')
                cursor.execute('DELETE FROM mining_fptree_fp')
                cursor.execute('DELETE FROM metrics_fp')
                cursor.execute(
                    '''UPDATE process 
                    SET fp_growth = %s, updated_at = %s
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
            
        return redirect(url_for('routes.fpgrowth'))

    @staticmethod
    def calculate_fpgrowth():
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get setup parameters with defaults
            cursor.execute('SELECT min_support_fp, min_confidance_fp FROM setups LIMIT 1')
            setup = cursor.fetchone() or {
                'min_support_fp': 0, 
                'min_confidance_fp': 0
            }
            
            # Get file info with defaults
            cursor.execute('SELECT * FROM file_infos LIMIT 1')
            file_info = cursor.fetchone() or {
                'filename': 'No file uploaded', 
                'count_transaction': 0, 
                'count_item': 0, 
                'year': 'N/A'
            }
            
            # Get frequent itemsets
            cursor.execute('SELECT * FROM frequent_fp')
            frequent_fp = cursor.fetchall()
            
            cursor.execute('SELECT * FROM detail_frequent_fp')
            detail_frequent_fp = cursor.fetchall()
            
            # Get association rules
            cursor.execute('SELECT * FROM association_rule_fp')
            association_rule = cursor.fetchall()
            
            # Get metrics with defaults
            cursor.execute('SELECT * FROM metrics_fp LIMIT 1')
            metric = cursor.fetchone() or {
                'execution_time': 'N/A', 
                'total_rules_found': 0, 
                'avg_lift': 0, 
                'avg_accuracy': 0
            }
            
            return render_template(
                'pages/calculate_fpgrowth.html',
                header_title='Perhitungan FP-Growth',
                frequent_fp=frequent_fp,
                detail_frequent_fp=detail_frequent_fp,
                association_rule=association_rule,
                metric=metric,
                file_info=file_info,
                setup=setup
            )
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.fpgrowth'))
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def process_index():
        cursor = None
        try:
            db = get_db()
            cursor = db.cursor()
            start_time = time.time()
            
            # Get process status
            cursor.execute('SELECT * FROM process LIMIT 1')
            process = cursor.fetchone()
            
            # Get setup parameters
            cursor.execute('SELECT min_support_fp, min_confidance_fp FROM setups LIMIT 1')
            setup = cursor.fetchone()
            if not setup:
                flash('Parameter setup belum diisi', 'error')
                return redirect(url_for('routes.fpgrowth'))
                
            min_support = setup[0]
            min_confidence = setup[1]

            # Get all transactions
            cursor.execute('SELECT code_transaction, item FROM data_transactions')
            transactions_data = cursor.fetchall()
            
            # Process transactions
            transactions = [row[1].split(', ') for row in transactions_data]
            transaction_codes = [row[0] for row in transactions_data]
            total_transactions = len(transactions)

            # ==================================
            # STEP 1: Frequent 1-itemsets
            # ==================================
            item_counts = defaultdict(int)
            for transaction in transactions:
                for item in transaction:
                    item_counts[item.strip()] += 1

            # Insert frequent header
            cursor.execute('INSERT INTO frequent_fp (name) VALUES (%s)', ('Frequent 1-itemset',))
            frequent_id = cursor.lastrowid
            
            # Store all 1-itemsets
            frequent_1_items = {}
            for item, count in item_counts.items():
                support = count / total_transactions
                is_frequent = support >= min_support
                description = 'Lolos' if is_frequent else 'Tidak Lolos'
                
                cursor.execute(
                    '''INSERT INTO detail_frequent_fp 
                    (item, transaction_count, support, description, frequent_id) 
                    VALUES (%s, %s, %s, %s, %s)''',
                    (item, count, round(support, 4), description, frequent_id)
                )
                
                if is_frequent:
                    frequent_1_items[item] = count

            # Sort frequent items by count (descending)
            sorted_items = sorted(frequent_1_items.items(), key=lambda x: (-x[1], x[0]))

            # ==================================
            # STEP 2: Item Initials
            # ==================================
            item_initials = {}
            used_initials = set()
            
            for item, count in sorted_items:
                # Generate initial from first letters of each word
                words = item.split()
                initial = ''.join([word[0].upper() for word in words])
                
                # Handle duplicates
                i = 1
                while initial in used_initials:
                    initial = initial + str(i)
                    i += 1
                used_initials.add(initial)
                item_initials[item] = initial
                
                # Calculate support
                support = count / total_transactions
                
                # Insert into item_initial_fp
                cursor.execute(
                    '''INSERT INTO item_initial_fp 
                    (item, is_initial, transaction_count, support) 
                    VALUES (%s, %s, %s, %s)''',
                    (item, initial, count, round(support, 4)))
            
            # Create reverse mapping for lookup
            initial_to_item = {v: k for k, v in item_initials.items()}

            # ==================================
            # STEP 3: Processed Transactions
            # ==================================
            for code, transaction in zip(transaction_codes, transactions):
                # Filter and sort items by frequency
                filtered_items = [item.strip() for item in transaction if item.strip() in frequent_1_items]
                filtered_items.sort(key=lambda x: (-frequent_1_items[x], x))
                
                # Convert to initials
                ordered_transaction = ', '.join([item_initials[item] for item in filtered_items])
                
                cursor.execute(
                    '''INSERT INTO transaction_process_fp 
                    (transaction_code, ordered_transaction) 
                    VALUES (%s, %s)''',
                    (code, ordered_transaction))
            
            # ==================================
            # STEP 4: FP-Tree Construction and Mining
            # ==================================
            class FPTreeNode:
                def __init__(self, name, count, parent):
                    self.name = name
                    self.count = count
                    self.parent = parent
                    self.children = {}
                    self.link = None
            
            # Build header table
            header_table = defaultdict(list)
            root = FPTreeNode(None, None, None)
            
            # Build FP-Tree
            for transaction in transactions:
                # Filter and sort items
                filtered_items = [item.strip() for item in transaction if item.strip() in frequent_1_items]
                filtered_items.sort(key=lambda x: (-frequent_1_items[x], x))
                
                # Update tree
                current_node = root
                for item in filtered_items:
                    if item in current_node.children:
                        child = current_node.children[item]
                        child.count += 1
                    else:
                        child = FPTreeNode(item, 1, current_node)
                        current_node.children[item] = child
                        
                        # Update header table
                        if header_table[item]:
                            last_node = header_table[item][-1]
                            last_node.link = child
                        header_table[item].append(child)
                    
                    current_node = child
            
            # Mining steps storage
            mining_steps = []
            
            def mine_tree(header_table, min_support_count, prefix, frequent_itemsets, level=0):
                # Sort items by frequency
                items = [item for item in header_table.keys()]
                items.sort(key=lambda x: (-frequent_1_items[x], x))
                
                for item in items:
                    # New itemset
                    new_prefix = prefix.copy()
                    new_prefix.add(item)
                    support_count = sum(node.count for node in header_table[item])
                    frequent_itemsets.append((new_prefix, support_count))
                    
                    # Conditional pattern base
                    conditional_patterns = []
                    for node in header_table[item]:
                        path = []
                        parent = node.parent
                        while parent.name is not None:
                            path.append(parent.name)
                            parent = parent.parent
                        if path:
                            conditional_patterns.append((path, node.count))
                    
                    # Store mining step
                    mining_steps.append({
                        'stage': 'Conditional Pattern Base',
                        'item': item,
                        'pattern_base': str([f"{path} (count: {count})" for path, count in conditional_patterns]),
                        'level': level,
                        'tree_item': item_initials[item]
                    })
                    
                    # Build conditional FP-Tree
                    conditional_header = defaultdict(list)
                    conditional_root = FPTreeNode(None, None, None)
                    
                    for path, count in conditional_patterns:
                        path.sort(key=lambda x: (-frequent_1_items[x], x))
                        for _ in range(count):
                            current_node = conditional_root
                            for item in path:
                                if item in current_node.children:
                                    child = current_node.children[item]
                                    child.count += 1
                                else:
                                    child = FPTreeNode(item, 1, current_node)
                                    current_node.children[item] = child
                                    
                                    if conditional_header[item]:
                                        last_node = conditional_header[item][-1]
                                        last_node.link = child
                                    conditional_header[item].append(child)
                                
                                current_node = child
                    
                    if conditional_header:
                        mining_steps.append({
                            'stage': 'Conditional FP-Tree',
                            'item': item,
                            'pattern_base': '',
                            'level': level,
                            'tree_item': ', '.join([item_initials[i] for i in conditional_header.keys()])
                        })
                        
                        # Recursive mining
                        mine_tree(conditional_header, min_support_count, new_prefix, frequent_itemsets, level+1)
                        
                        mining_steps.append({
                            'stage': 'Frequent Itemset',
                            'item': item,
                            'pattern_base': '',
                            'level': level,
                            'tree_item': ', '.join([item_initials[i] for i in new_prefix])
                        })
            
            # Mine the FP-Tree
            frequent_itemsets = []
            mine_tree(header_table, min_support * total_transactions, set(), frequent_itemsets)
            
            # Store mining steps
            for step in mining_steps:
                cursor.execute(
                    '''INSERT INTO mining_fptree_fp 
                    (stage, item, pattern_base, level, tree_item) 
                    VALUES (%s, %s, %s, %s, %s)''',
                    (step['stage'], step['item'], step['pattern_base'], step['level'], step['tree_item'])
                )
            
            # ==================================
            # STEP 5: Association Rules
            # ==================================
            rules = []
            for itemset, support_count in frequent_itemsets:
                itemset = list(itemset)
                if len(itemset) > 1:
                    support = support_count / total_transactions
                    
                    for i in range(1, len(itemset)):
                        for antecedent in combinations(itemset, i):
                            antecedent = set(antecedent)
                            consequent = set(itemset) - antecedent
                            
                            # Find antecedent support
                            antecedent_support = 0
                            for itemset2, count in frequent_itemsets:
                                if antecedent.issubset(itemset2):
                                    antecedent_support = count / total_transactions
                                    break
                        
                            # Calculate confidence
                            confidence = support / antecedent_support if antecedent_support > 0 else 0
                        
                            if confidence >= min_confidence:
                                # Find consequent support
                                consequent_support = 0
                                for itemset2, count in frequent_itemsets:
                                    if consequent.issubset(itemset2):
                                        consequent_support = count / total_transactions
                                        break
                                
                                # Calculate metrics
                                lift = confidence / consequent_support if consequent_support > 0 else 0
                                correlation = "Positif" if lift > 1 else "Negatif" if lift < 1 else "Netral"
                                precision = confidence
                                recall = precision
                                accuracy = (precision + recall) / 2
                                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                                
                                # Convert to item names
                                antecedent_names = []
                                for a in antecedent:
                                    try:
                                        antecedent_names.append(initial_to_item[a])
                                    except KeyError:
                                        antecedent_names.append(a)
                                
                                consequent_names = []
                                for c in consequent:
                                    try:
                                        consequent_names.append(initial_to_item[c])
                                    except KeyError:
                                        consequent_names.append(c)
                                
                                rule_str = f"{antecedent_names} => {consequent_names}"
                                
                                rules.append({
                                    'rule': rule_str,
                                    'support_a': round(antecedent_support, 4),
                                    'support_b': round(support, 4),
                                    'confidence': round(confidence, 4),
                                    'lift': round(lift, 4),
                                    'correlation': correlation,
                                    'accuracy': round(accuracy, 4),
                                    'precision': round(precision, 4),
                                    'recall': round(recall, 4),
                                    'f1_score': round(f1_score, 4)
                                })
            
            # Store association rules
            for rule in rules:
                cursor.execute(
                    '''INSERT INTO association_rule_fp 
                    (rule, support_a, support_b, confidence, lift, correlation, accuracy, precision_val, recall_val, f1_score_val) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (rule['rule'], rule['support_a'], rule['support_b'], rule['confidence'], 
                    rule['lift'], rule['correlation'], rule['accuracy'], rule['precision'], 
                    rule['recall'], rule['f1_score'])
                )
            
            # ==================================
            # STEP 6: Metrics
            # ==================================
            execution_time = round(time.time() - start_time, 2)
            num_rules = len(rules)
            avg_lift = sum(rule['lift'] for rule in rules) / num_rules if num_rules > 0 else 0
            avg_accuracy = sum(rule['accuracy'] for rule in rules) / num_rules if num_rules > 0 else 0
            
            cursor.execute(
                '''INSERT INTO metrics_fp 
                (execution_time, total_rules_found, avg_lift, avg_accuracy) 
                VALUES (%s, %s, %s, %s)''',
                (f"{execution_time} seconds", num_rules, round(avg_lift, 4), round(avg_accuracy, 4))
            )
            
            # Update process status
            if process:
                cursor.execute(
                    'UPDATE process SET fp_growth = %s, updated_at = %s WHERE id = %s',
                    (True, datetime.now(), process[0])
                )
            
            db.commit()
            flash('Berhasil diproses perhitungan FP-Growth. Lihat hasil perhitungan.', 'success')
            return redirect(url_for('routes.fpgrowth'))

        except Exception as e:
            db.rollback()
            flash(f'Gagal memproses FP-Growth: {str(e)}', 'danger')
            return redirect(url_for('routes.fpgrowth'))
        finally:
            if cursor:
                cursor.close()
# ResultController.py
from flask import flash, url_for, session, redirect, render_template
from apps.database.database import get_db

class ResultController:
    @staticmethod
    def result_index():
        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            
            # Get metrics for Apriori
            cursor.execute('''SELECT 
                    CAST(SUBSTRING_INDEX(execution_time, ' ', 1) AS DECIMAL(10,2)) as exec_time_value,
                    total_rules_found, 
                    avg_lift, 
                    avg_accuracy 
                FROM metrics_ap 
                ORDER BY id DESC 
                LIMIT 1''')
            metrics_ap = cursor.fetchone()
            
            # Get metrics for FP-Growth
            cursor.execute('''SELECT 
                    CAST(SUBSTRING_INDEX(execution_time, ' ', 1) AS DECIMAL(10,2)) as exec_time_value,
                    total_rules_found, 
                    avg_lift, 
                    avg_accuracy 
                FROM metrics_fp 
                ORDER BY id DESC 
                LIMIT 1''')
            metrics_fp = cursor.fetchone()
            
            # Get setup parameters
            cursor.execute('SELECT min_support_ap, min_confidance_ap, min_support_fp, min_confidance_fp FROM setups LIMIT 1')
            setup = cursor.fetchone()
            
            # Format the data for visualization
            if metrics_ap and metrics_fp:
                # Convert accuracy percentages for pie chart (normalized to 100)
                ap_accuracy = round(metrics_ap[3] * 100, 2) if metrics_ap[3] else 0
                fp_accuracy = round(metrics_fp[3] * 100, 2) if metrics_fp[3] else 0
                
                # Perbaikan: Hapus koma di akhir baris ini
                apriori_normalized = float(round((ap_accuracy / (ap_accuracy + fp_accuracy)) * 100, 2))
                fp_growth_normalized = float(round((fp_accuracy / (ap_accuracy + fp_accuracy)) * 100, 2))
                
                # Create a new dictionary with formatted metrics
                formatted_metrics_ap = {
                    'exec_time': metrics_ap[0],
                    'total_rules': metrics_ap[1],
                    'avg_lift': metrics_ap[2],
                    'avg_accuracy': apriori_normalized  # formatted as percentage
                }
                
                formatted_metrics_fp = {
                    'exec_time': metrics_fp[0],
                    'total_rules': metrics_fp[1],
                    'avg_lift': metrics_fp[2],
                    'avg_accuracy': fp_growth_normalized  # formatted as percentage
                }
                
                return render_template('pages/result.html', 
                                    header_title='Hasil', 
                                    user=user,
                                    metrics_ap=formatted_metrics_ap, 
                                    metrics_fp=formatted_metrics_fp, 
                                    setup=setup)
            
            return render_template('pages/result.html', 
                                header_title='Hasil', 
                                user=user,
                                metrics_ap=None, 
                                metrics_fp=None, 
                                setup=setup)
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('routes.result'))
        finally:
            if cursor:
                cursor.close()
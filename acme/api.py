import os
import pandas as pd
import psycopg2
from flask import Flask, request, send_from_directory, render_template
from werkzeug.utils import redirect

db_params = {}

app = Flask(__name__)

#  Куда сохраняем
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Загрузка и сохранение в uploaded
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)
        return redirect('/')
    # # отображение списка скаченных файлов
    # files = os.listdir(UPLOAD_FOLDER)
    # return render_template(template_name_or_list='/', files=files)

# удаление
@app.route ('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect ('/')

# параметры БД
@app.route('/set_params', methods=['POST'])
def set_params():
    global db_params
    db_params['host'] = request.form['host']
    db_params['port'] = request.form['port']
    db_params['database'] = request.form['database']
    db_params['user'] = request.form['user']
    db_params['password'] = request.form['password']
    db_params['table_name'] = request.form['table_name']
    return redirect('/')
# Работа с БД
@app.route('/download_table')
def download_table():
    try:
        if not db_params:
            return "Параметры на подключение не введены"
        # подключение
        conn = psycopg2.connect(
            host=db_params['host'],
            port=db_params['port'],
            database=db_params['database'],
            user=db_params['user'],
            password=db_params['password']
        )

        # чтение таблицы
        table_name = db_params['table_name']  # название таблицы
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # сохранение в CSV
        filename = f'load_{table_name}.csv'
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        df.to_csv(save_path, index=False)

        return redirect('/')
    except Exception as e:
        return f"Ошибка: {str(e)}"

# -стартовая страница
@app.route('/', methods=['GET'])
def index():
    # отображение списка скаченных файлов
    files = os.listdir(UPLOAD_FOLDER)
    return render_template(template_name_or_list='base.html', files=files)





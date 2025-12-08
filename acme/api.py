import os
import pandas as pd
import psycopg2
import io
import matplotlib.pyplot as plt

from flask import Flask, request, render_template, send_file
from werkzeug.utils import redirect
from models import *




app = Flask(__name__)

db_params = {}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mihail:Qwerty12345@localhost:5432/data_flask'
db.init_app(app)

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

@app.route('/analyze_salary')
def analyze_salary():
    with app.app_context():
        salaries = Salary_developer.query.all()

        if not salaries:
            return render_template(template_name_or_list='base.html', analysis_results=None, files=os.listdir(UPLOAD_FOLDER))
        df = pd.DataFrame([{
            'id': s.id,
            'post': s.post,
            'salary': s.salary
        } for s in salaries])

    mean_salary = df['salary'].mean()
    median_salary = df['salary'].median()
    correlation = df[['id', 'salary']].corr().iloc[0, 1]

    analysis_results = {
        'mean_salary': round(mean_salary, 2),
        'median_salary': round(median_salary, 2),
        'correlation': round(correlation, 2)
    }

    # Передача в шаблон
    return render_template(template_name_or_list='base.html',
                           analysis_results=analysis_results,
                           files=os.listdir(UPLOAD_FOLDER))


@app.route('/plot')
def plot_salary():
    # Получение данных из базы
    salaries = Salary_developer.query.all()
    if not salaries:
        return "Нет данных для построения графика."

    df = pd.DataFrame([{
        'id': s.id,
        'post': s.post,
        'salary': s.salary
    } for s in salaries])

    # Построение графика
    plt.figure(figsize=(12,7))
    df.groupby('post')['salary'].mean().sort_values().plot(kind='bar')
    plt.title('Средняя зарплата по должностям')
    plt.ylabel('Зарплата')
    plt.xlabel('Должность')

    plt.tight_layout()

    # Сохраняем
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Возвращаем изображение
    return send_file(buf, mimetype='image/png')

@app.route('/generate_report')
def generate_report():
    # Создаем DataFrame с данными зарплат
    salaries = Salary_developer.query.all()
    if not salaries:
        df = pd.DataFrame(columns=['ID', 'Должность', 'Зарплата'])
    else:
        df = pd.DataFrame([{
            'ID': s.id,
            'Должность': s.post,
            'Зарплата': s.salary
        } for s in salaries])

    # Создаем байтовый поток для Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Зарплаты')
    buffer.seek(0)

    # сохраняем файл xlsx
    return send_file(
        io.BytesIO(buffer.getvalue()),
        as_attachment=True,
        download_name='salary_report.xlsx',
        mimetype='application/vnd.openpyxl.spreadsheetml.sheet'
    )

# -стартовая страница
@app.route('/', methods=['GET'])
def index():
    # отображение списка скаченных файлов
    files = os.listdir(UPLOAD_FOLDER)
    return render_template(template_name_or_list='base.html', files=files)

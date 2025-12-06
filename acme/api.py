import os
from flask import Flask, request, send_from_directory, render_template
from werkzeug.utils import redirect

app = Flask(__name__)

#  Куда сохраняем
UPLOAD_FOLDER = 'C:/Users/Olga/mu_code/API_Flask/uploaded'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Загрузка и сохранение в uploaded
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(save_path)
        return redirect('/upload')
    # отображение списка скаченных файлов
    files = os.listdir(UPLOAD_FOLDER)
    return render_template(template_name_or_list='upload.html', files=files)

# удаление
@app.route ('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect ('/upload')

# -стартовая страница
@app.route('/', methods=['GET'])
def index():
    return render_template(template_name_or_list='base.html')




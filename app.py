import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Memuat environment variables dari file .env
load_dotenv()

app = Flask(__name__)

# --- KONFIGURASI APLIKASI ---
app.secret_key = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM manhwas ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', manhwas=data)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        rating = request.form['rating']
        status = request.form['status']

        if 'image' not in request.files:
            # FIX: Terjemahan pesan notifikasi
            flash('Tidak ada bagian file yang diunggah.')
            return redirect(request.url)
        
        file = request.files['image']

        if file.filename == '':
            # FIX: Terjemahan pesan notifikasi
            flash('Tidak ada file yang dipilih.')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO manhwas (title, genre, rating, status, image) VALUES (%s, %s, %s, %s, %s)",
                        (title, genre, rating, status, filename))
            mysql.connection.commit()
            cur.close()
            
            flash('Manhwa berhasil ditambahkan!')
            return redirect(url_for('index'))
        else:
            flash('Tipe file tidak diizinkan!')
            return redirect(request.url)

    return render_template('form.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT image FROM manhwas WHERE id = %s", [id])
    image_to_delete = cur.fetchone()
    
    cur.execute("DELETE FROM manhwas WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    if image_to_delete and image_to_delete[0]:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete[0])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    flash('Manhwa berhasil dihapus.')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit_form(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM manhwas WHERE id = %s", [id])
    data = cur.fetchone()
    cur.close()
    if data:
        # Menggunakan template edit_modal.html yang sudah diperbaiki
        return render_template('edit_form.html', manhwa=data)
    return 'Data tidak ditemukan!', 404

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    title = request.form['title']
    genre = request.form['genre']
    rating = request.form['rating']
    status = request.form['status']

    cur = mysql.connection.cursor()

    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("""
                UPDATE manhwas SET title=%s, genre=%s, rating=%s, status=%s, image=%s
                WHERE id=%s
            """, (title, genre, rating, status, filename, id))
        else:
            flash('Tipe file baru tidak diizinkan!')
            return redirect(url_for('edit_form', id=id))
    else:
        cur.execute("""
            UPDATE manhwas SET title=%s, genre=%s, rating=%s, status=%s
            WHERE id=%s
        """, (title, genre, rating, status, id))
    
    mysql.connection.commit()
    cur.close()
    flash('Manhwa berhasil diupdate!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, request, redirect, url_for
import os
from database import getConnection

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/images'

menu = [
    {"id": 1, "link": "/", "text": "Home"},
    {"id": 2, "link": "/contact", "text": "Contact Us"},
    {"id": 3, "link": "/addList", "text": "+ New List"},
]

@app.route("/")
def home():
    db = getConnection()  
    sqlstr = f"SELECT * from items"
    cur = db.cursor()
    cur.execute(sqlstr)
    output_json = cur.fetchall()
    print(output_json)
    return render_template("index.html", menu=menu, list=output_json)

@app.route("/contact")
def contact():
    return render_template("contact.html", menu=menu)

@app.route("/detail/<int:id>")
def detail(id):
    db = getConnection()  
    sqlstr = f"SELECT * from items where id = {id}"
    cur = db.cursor()
    cur.execute(sqlstr)
    output_json = cur.fetchall()
    print(output_json)
    return render_template('detail.html', menu=menu, list=output_json)

@app.route("/addList", methods=['POST','GET'])
def addList():
    db = getConnection()
    if request.method == "POST":
        data = request.form.to_dict()
        file = request.files['image_content']
        data['image_content'] = file.filename
        if file == None:
            print("masukin gambarnya bang")
        print(data)
        try:
            cur = db.cursor()
            
            # Periksa apakah title sudah ada dalam database
            cur.execute(f"SELECT title FROM items WHERE title = '{data['title']}'")
            existing_title = cur.fetchone()
            
            # jika sudah ada maka arahkan ke error page
            if existing_title:
                return errorPage()
            
            # Jika title belum ada, lakukan insert
            sqlstr = f"INSERT INTO items (title, description, image_name) VALUES('{data['title']}', '{data['desc']}', '{data['image_content']}')"
            cur.execute(sqlstr)
            db.commit()
            cur.close()
            file.save(os.path.join('static/images', file.filename))
        except Exception as e:
            print("Error in SQL : \n", e)
        finally:
            db.close()
        return redirect(url_for('home'))
    return render_template("add.html", menu=menu)


@app.route("/delete/<int:id>")
def delete(id):
    db = getConnection()  # fungsi yang dipanggil sesuai dengan url diatas
    sqlstr = f"DELETE from items where id = {id}"
    cur = db.cursor()
    cur.execute(sqlstr)
    db.commit()
    cur.close()
    return redirect(url_for('home'))

@app.route("/update/<int:id>", methods=['POST', 'GET'])
def update(id):
    db = getConnection()
    if request.method == "POST":
        data = request.form.to_dict()
        image = request.files['image_content']
        try:
            cur = db.cursor()
            
            # Periksa apakah title yang baru sudah ada dalam database (kecuali jika title tidak diubah)
            cur.execute(f"SELECT title FROM items WHERE title = '{data['title']}'")
            existing_title = cur.fetchone()
            
            if existing_title:
                return errorPage()
            
            if image.filename:
                print("TRUE")
                cur.execute(f"UPDATE items SET image_name = '{image.filename}' WHERE id = {id}")
                db.commit()
                image.save(os.path.join('static/images', image.filename))
            sqlstr = f"UPDATE items SET title = '{data['title']}', description = '{data['desc']}' WHERE id = {id}"
            cur.execute(sqlstr)
            db.commit()
            print(data['title'], "-------------------------------")
        except Exception as e:
            print("Error in SQL : \n", e)
        finally:
            db.close()
        return redirect(url_for('home'))
    else:
        sqlstr = f"SELECT * from items where id = {id}"
        cur = db.cursor()
        cur.execute(sqlstr)
        output_json = cur.fetchall()

        print(output_json)
        return render_template('update.html', menu=menu, list=output_json)

@app.route("/error")
def errorPage():
    return render_template('error.html', menu=menu)

app.run(debug=True)
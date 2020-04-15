import os
import sqlite3
import sys
from flask import Flask, render_template, request, g, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
here = os.path.dirname(__file__)
DATABASE = os.path.join(here, 'sqlite_db/database.db')
IMAGE_FOLDER = os.path.join(here, 'static/images/')
VIDEO_FOLDER = os.path.join(here, 'static/videos/')


def get_db_cursor():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db, db.cursor()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def landing_page():
    return render_template("landing.html")

@app.route('/create', methods=["GET"])
def create():
    return render_template("create.html")

@app.route('/explore', methods=["GET"])
def explore():
    result = []
    with app.app_context():
        db, cur = get_db_cursor()
        query_sql = "select * from GRAPHY"
        cur.execute(query_sql)
        rows = cur.fetchall()
        for row in rows:
            dictionary = {
                'id': row[0],
                'title': row[1],
                'image_name': row[2],
            }
            result.append(dictionary)
    return render_template("explore.html", graphies=result)

@app.route('/image/<filename>')
def send_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/chapters/video/<video_path>')
def send_video(video_path):
    return send_from_directory(VIDEO_FOLDER, video_path)

def get_chp_details(form, files, graphy_id):
    chp_dict = {}
    for key in form:
        if key.startswith('chp_title'):
            id = int(key.replace('chp_title', ''))
            if id not in chp_dict:
                chp_dict[id] = {}
            chp_dict[id]['heading'] = form[key]
        elif key.startswith('chp_description'):
            id = int(key.replace('chp_description', ''))
            if id not in chp_dict:
                chp_dict[id] = {}
            chp_dict[id]['description'] = form[key]

    for key in files:
        if key.startswith('chp_video'):
            id = int(key.replace('chp_video', ''))
            if id not in chp_dict:
                chp_dict[id] = {}
            chp_dict[id]['video_path'] = files[key].filename
    result = []

    for key, value_dict in sorted(chp_dict.items()):
        if set(("heading", "description", "video_path")) > set(value_dict.keys()):
            # Skip over incomplete chapters
            continue
        tup = (value_dict['heading'], value_dict['description'], value_dict['video_path'], graphy_id)
        result.append(tup)

    return result

def sanitize_files(files):
    # We require atleast the title and photo of a new graphy, chapters are optional
    # Also check videos are mp4 or avi
    # return false if above conditions is not true
    #TODO: check more cases for proper sanitization

    for key in files:

        try:
            filename, file_extension = os.path.splitext(files[key].filename)
        except:
            return False

        if file_extension not in ['.png', '.jpg', '.jpeg', '.mp4', '.avi']:
            return False

    return True

def sanitize_form(form):
    title = form.get('title')
    if not title:
        return False
    return True

@app.route('/upload', methods=["POST"])
def upload():
    # Save the upload and redirect
    if request.method != 'POST' or not sanitize_files(request.files) or not sanitize_form(request.form):
        return render_template("create.html", message="The input data is not correct!")

    photo = request.files['photo']
    title = request.form.get('title')
    photo.save(os.path.join(IMAGE_FOLDER, photo.filename))

    with app.app_context():
        db, cur = get_db_cursor()
        # Free from sql injection like attacks
        insert_sql = "INSERT INTO GRAPHY(title, image_path) VALUES (?, ?)"
        data_tuple = (title, photo.filename)
        cur.execute(insert_sql, data_tuple)

        # Get graphy_id and insert chapters, if provided
        cur.execute('SELECT last_insert_rowid()')
        graphy_id = cur.fetchone()[0]
        data_tuple_list = get_chp_details(request.form, request.files, graphy_id)
        insert_chapters_in_db(data_tuple_list, request.files, cur)

        # Commit at last for transaction
        db.commit()
        print("Success!!")
    return render_template("upload.html")

def insert_chapters_in_db(data_list, files, cursor):
    counter = 1
    for data in data_list:

        # data is sorted, so saving videos one by one
        video = files.get('chp_video' + str(counter))
        if video:
            video.save(os.path.join(VIDEO_FOLDER, video.filename))

        insert_sql = "INSERT INTO CHAPTER(heading, description, video_path, graphy_id) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_sql, data)
        counter += 1

def fetch_chapters_from_db(cursor, graphy_id):
    result = []
    cursor.execute("select * from CHAPTER where graphy_id=?", (graphy_id,))
    rows = cursor.fetchall()
    for row in rows:
        dictionary = {
            'heading': row[1],
            'description': row[2],
            'video_path': row[3],
        }
        result.append(dictionary)
    return result

@app.route('/upload-chapter/<graphy_id>', methods=['POST'])
def upload_chapter(graphy_id):
    chapter_tuple = get_chp_details(request.form, request.files, graphy_id)
    with app.app_context():
        db, cur = get_db_cursor()
        insert_chapters_in_db(chapter_tuple, request.files, cur)

        db.commit()

    return redirect(url_for('get_chapters', graphy_id=graphy_id))

@app.route('/chapters/<graphy_id>', methods=["GET"])
def get_chapters(graphy_id):
    result = []
    with app.app_context():
        db, cur = get_db_cursor()
        result = fetch_chapters_from_db(cur, graphy_id)

    return render_template("chapters.html", chapters=result, graphy_id=graphy_id)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port)
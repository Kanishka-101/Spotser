from flask import Flask, request, render_template, redirect, session, url_for, send_file
import json
import os
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'spotser_admin_secret'  # Change this to a random string

DATA_FILE = 'data/contacts.json'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    review = request.form.get('review')

    new_data = {
        'name': name,
        'email': email,
        'message': message,
        'review': review
    }

    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        data.append(new_data)
        f.seek(0)
        json.dump(data, f, indent=4)

    return redirect('/thankyou')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            session['admin'] = True
            return redirect('/entries')
        else:
            return render_template('login.html', error='Incorrect password')
    return render_template('login.html')

@app.route('/entries')
def view_entries():
    if not session.get('admin'):
        return redirect('/login')
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    return render_template('entries.html', entries=data)

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if not session.get('admin'):
        return redirect('/login')
    try:
        with open(DATA_FILE, 'r+') as f:
            data = json.load(f)
            if 0 <= entry_id < len(data):
                data.pop(entry_id)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
    except Exception as e:
        print("Error deleting entry:", e)
    return redirect('/entries')

@app.route('/download')
def download_csv():
    if not session.get('admin'):
        return redirect('/login')
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if not data:
        return "No data to download."

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=['name', 'email', 'message', 'review'])
    writer.writeheader()
    writer.writerows(data)

    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='contact_submissions.csv'
    )
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

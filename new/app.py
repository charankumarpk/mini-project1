from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models.data import *
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

# Initialize SQLAlchemy with the app
db.init_app(app)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/laptops")
def laptops():
    device = Data.query.all()
    print(f"Devices fetched: {device}")
    return render_template("laptops.html", content=device)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin':  # Fixed password
            session['authenticated'] = True
            return redirect('/admin')  # Redirect to admin page after successful login
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Logout clears session and redirects to login page
    session.pop('authenticated', None)
    return redirect('/login')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'authenticated' not in session or not session['authenticated']:
        return redirect('/login')  # Redirect to login if session is not authenticated

    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'a':
            devices = Data.query.all()
            return render_template('admin.html', content=devices)
        else:
            return render_template('password_prompt.html', error="Invalid password")

    # Render the password prompt every time
    return render_template('password_prompt.html')



@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


@app.route("/thank")
def thank():
    return render_template("thank.html")


@app.route("/submit", methods=['POST'])
def submit():
    form_data = request.form.to_dict()
    print(f"form_data: {form_data}")

    name = form_data.get('Name')
    brand = form_data.get('brand')
    processor = form_data.get('processor')
    ram = form_data.get('ram')
    storage = form_data.get('storage')
    category = form_data.get('category')
    description = form_data.get('description')
    price = form_data.get('price')

    # Handle the image upload
    pic_filename = None
    if 'pic' in request.files:
        pic = request.files['pic']
        if pic and allowed_file(pic.filename):
            pic_filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))

    # Check if the device exists
    device = Data.query.filter_by(Name=name).first()
    if not device:
        device = Data(
            Name=name,
            brand=brand,
            processor=processor,
            ram=ram,
            storage=storage,
            category=category,
            description=description,
            price=price,
            pic=pic_filename,
        )
        db.session.add(device)
        db.session.commit()
    print("Submitted successfully")
    return redirect('/admin')


@app.route('/delete/<int:id>', methods=['GET', 'DELETE'])
def delete(id):
    device = Data.query.get(id)
    if not device:
        return jsonify({'message': 'Device not found'}), 404

    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred while deleting the data: {e}'}), 500


@app.route('/add', methods=['POST'])
def add_device():
    try:
        data = request.get_json()

        pic_filename = None
        if 'pic' in request.files:
            pic = request.files['pic']
            if pic and allowed_file(pic.filename):
                pic_filename = secure_filename(pic.filename)
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))

        device = Data(
            Name=data.get('Name'),
            brand=data.get('brand'),
            processor=data.get('processor'),
            ram=data.get('ram'),
            storage=data.get('storage'),
            category=data.get('category'),
            description=data.get('description'),
            price=data.get('price'),
            pic=pic_filename,
        )

        db.session.add(device)
        db.session.commit()

        return jsonify({'message': 'Device added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_device(id):
    device = Data.query.get_or_404(id)

    if request.method == 'POST':
        device.Name = request.form['Name']
        device.brand = request.form['brand']
        device.processor = request.form['processor']
        device.ram = request.form['ram']
        device.storage = request.form['storage']
        device.category = request.form['category']
        device.description = request.form['description']
        device.price = request.form['price']

        pic_filename = device.pic
        if 'pic' in request.files:
            pic = request.files['pic']
            if pic and allowed_file(pic.filename):
                pic_filename = secure_filename(pic.filename)
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))

        device.pic = pic_filename

        try:
            db.session.commit()
            return redirect('/admin')
        except Exception as e:
            db.session.rollback()
            return f"There was an issue while updating the record: {str(e)}"

    return render_template('update.html', device=device)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

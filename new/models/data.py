
from utils.db import db


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    processor = db.Column(db.String(100))
    ram = db.Column(db.String(50))
    storage = db.Column(db.String(50))
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    pic = db.Column(db.String(200))  # Store the path to the image file

    # Optionally, you can add a method to handle image URL generation
    def get_pic_url(self):
        return f'/static/images/{self.pic}'  # Assuming images are stored in the 'static/images' directory

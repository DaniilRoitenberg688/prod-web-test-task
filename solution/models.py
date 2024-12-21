from werkzeug.security import generate_password_hash, check_password_hash
from config import db


class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    alpha2 = db.Column(db.String(3))
    alpha3 = db.Column(db.String(4))
    region = db.Column(db.String(80))

    def to_dict(self):
        return {
            'name': self.name,
            'alpha2': self.alpha2,
            'alpha3': self.alpha3,
            'region': self.region
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(31))
    email = db.Column(db.String(51))
    password = db.Column(db.String())
    country_code = db.Column(db.String(3), db.ForeignKey('countries.alpha2'))
    is_public = db.Column(db.Boolean())
    phone = db.Column(db.String(21))
    image = db.Column(db.String(201))
    last_password_set = db.Column(db.Integer())

    def __init__(self, login, email, country_code, is_public, phone, image, last_password_set):
        self.login = login
        self.email = email
        self.country_code = country_code
        self.is_public = is_public
        self.phone = phone
        self.image = image
        self.last_password_set = last_password_set

    def set_password(self, password: str):
        if len(password) < 6:
            return 0, 'length error'
        if not (set(password) & set('qwertyuiopasdfghjklzxcvbnm')):
            return 0, 'no latin symbols'
        if not (set(password) & set('1234567890')):
            return 0, 'no numbers'
        self.password = generate_password_hash(password)
        return 1, ''

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        user = {'login': self.login,
                'email': self.email,
                'countryCode': self.country_code,
                'isPublic': self.is_public,
                'phone': self.phone}
        if self.image:
            user['image'] = self.image

        return user


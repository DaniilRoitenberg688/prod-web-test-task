from functools import wraps

from flask import jsonify, request
import jwt
from config import app, db
from models import User, Country
import time


def requires_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({'reason': 'Missing token'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            return jsonify({'reason': 'error while decode token'}), 401

        user_id = payload.get('user_id')
        created_at = payload.get('created_at')

        if not user_id or not created_at:
            return jsonify({'reason': 'Invalid token'}), 401

        user: User = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'reason': 'User not found'}), 401

        if created_at + 60 * 60 * 24 < int(time.time()):
            return jsonify({'reason': 'Token expired'}), 401

        if created_at < user.last_password_set:
            print(created_at, user.last_password_set)
            return jsonify({'reason': 'not valid token'}), 401

        return func(user, *args, **kwargs)

    return wrapper


@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200


@app.route('/api/countries', methods=['GET'])
def countries():
    regions = request.args.getlist('region')
    answer = Country.query.all()
    if regions:
        answer = Country.query.filter(Country.region.in_(regions)).all()

    if not answer:
        return jsonify({'reason': 'not found'}), 400

    answer = [i.to_dict() for i in answer]
    return jsonify(answer), 200


@app.route('/api/countries/<alpha2>')
def counties_by_alpha(alpha2):
    answer = Country.query.filter_by(alpha2=alpha2).first()
    if answer is None:
        return jsonify({'reason': 'not found'}), 404
    answer = answer.to_dict()
    return jsonify(answer), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    new_user_data = request.json
    print(new_user_data)
    login = new_user_data.get('login', '')
    email = new_user_data.get('email', '')
    password = new_user_data.get('password', '')
    country_code = new_user_data.get('countryCode', '')
    is_public = new_user_data.get('isPublic', True)
    phone = new_user_data.get('phone', '')
    image = new_user_data.get('image', '')

    if not login or not email or not password or not country_code:
        return jsonify({'reason': 'missing data'}), 400

    if not Country.query.filter_by(alpha2=country_code).first():
        return jsonify({'reason': 'no such country'}), 400

    if phone[0] != '+':
        return jsonify({'reason': 'bad phone number'}), 400

    if len(image) > 200:
        return jsonify({'reason': 'too long image'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'reason': 'not uniq email'}), 409

    if User.query.filter_by(login=login).first():
        return jsonify({'reason': 'not uniq login'}), 409

    if User.query.filter_by(phone=phone).first():
        return jsonify({'reason': 'not uniq phone'}), 409



    new_user = User(login=login,
                    email=email,
                    country_code=country_code,
                    is_public=is_public,
                    image=image,
                    phone=phone,
                    last_password_set=time.time())

    status, message = new_user.set_password(password)
    if not status:
        return jsonify({'reason': message}), 400

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'profile': new_user.to_dict()}), 201


@app.route('/api/auth/sign-in', methods=['POST'])
def login():
    data = request.get_json()
    print(data)
    user_login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({'reason': 'missing data'}), 400

    user: User = User.query.filter_by(login=user_login).first()
    if not user:
        return jsonify({'reason': 'no such user'}), 401
    if not user.check_password(password):
        return jsonify({'reason': 'wrong password'}), 401

    token = jwt.encode({'user_id': user.id, 'created_at': int(time.time())}, app.config['SECRET_KEY'],
                       algorithm='HS256')

    return jsonify({'token': token}), 200


@app.route('/api/me/profile', methods=['GET'])
@requires_user
def profile(user):
    return jsonify(user.to_dict()), 200


@app.route('/api/me/profile', methods=['PATCH'])
@requires_user
def change_profile(user):
    new_user_data = request.get_json()
    login = new_user_data.get('login', '')
    email = new_user_data.get('email', '')
    country_code = new_user_data.get('countryCode', '')
    is_public = new_user_data.get('isPublic', None)
    phone = new_user_data.get('phone', '')
    image = new_user_data.get('image', '')

    if login:
        if User.query.filter_by(login=login).first():
            return jsonify({'reason': 'not uniq login'}), 401
        user.login = login
        db.session.commit()

    if email:
        if User.query.filter_by(email=email).first():
            return jsonify({'reason': 'not uniq email'}), 401
        user.email = email
        db.session.commit()

    if country_code:
        if not Country.query.filter_by(alpha2=country_code).first():
            return jsonify({'reason': 'no such country'}), 400
        user.country_code = country_code
        db.session.commit()

    if is_public is not None:
        user.is_public = is_public
        db.session.commit()

    if phone:
        if phone[0] != '+':
            return jsonify({'reason': 'wrong phone format'}), 400
        if User.query.filter_by(phone=phone).first():
            return jsonify({'reason': 'not uniq phone number'}), 401

        user.phone = phone
        db.session.commit()

    if image:
        if len(image) > 200:
            return jsonify({'reason': 'too big image'}), 400
        user.image = image
        db.session.commit()

    return jsonify(user.to_dict()), 200


@app.route('/api/profiles/<login>', methods=['GET'])
@requires_user
def one_profile(user, login):
    if login == user.login:
        return jsonify(user.to_dict()), 200
    searching_user: User = User.query.filter_by(login=login).first()

    if not searching_user:
        return jsonify({'reason': 'no user with such login'}), 403

    if not searching_user.is_public:
        return jsonify({'reason': 'not public profile'}), 403

    return jsonify(searching_user.to_dict()), 200


@app.route('/api/me/updatePassword', methods=['POST'])
@requires_user
def update_password(user):
    data = request.get_json()
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    if not user.check_password(old_password):
        return jsonify('reason', 'old password error'), 403

    result, message = user.set_password(new_password)
    if not result:
        return jsonify({'reason': message}), 400

    user.last_password_set = time.time()
    db.session.commit()
    return jsonify({'status': 'ok'}), 200










if __name__ == "__main__":
    app.run(port=57424, debug=True)

from flask import jsonify, request
from config import app, db
from models import User, Country




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

    new_user = User(login=login,
                    email=email,
                    country_code=country_code,
                    is_public=is_public,
                    image=image,
                    phone_number=phone)

    status, message = new_user.set_password(password)
    if not status:
        return jsonify({'reason': message}), 400

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'profile': new_user.to_dict()}), 201



if __name__ == "__main__":

    app.run(port=57424, debug=True)


#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

# GET all bakeries or POST a new bakery
@app.route('/bakeries', methods=['GET', 'POST'])
def bakeries():
    if request.method == 'GET':
        bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
        return jsonify(bakeries), 200
    elif request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_bakery = Bakery(name=name)
            db.session.add(new_bakery)
            db.session.commit()
            return jsonify(new_bakery.to_dict()), 201
        else:
            return jsonify({'error': 'Missing name parameter'}), 400

# GET a bakery by id or PATCH (update) a bakery by id
@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(bakery.to_dict()), 200
    
    elif request.method == 'PATCH':
        name = request.form.get('name')
        if name:
            bakery.name = name
            db.session.commit()
            return jsonify(bakery.to_dict()), 200
        else:
            return jsonify({'error': 'Missing name parameter'}), 400

# DELETE a baked good by id
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get_or_404(id)
    
    db.session.delete(baked_good)
    db.session.commit()
    
    return jsonify({'message': 'Successfully deleted.'}), 200

# POST a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = float(request.form.get('price')) if request.form.get('price') else None
    
    if name and price is not None:
        new_baked_good = BakedGood(name=name, price=price)
        db.session.add(new_baked_good)
        db.session.commit()
        return jsonify(new_baked_good.to_dict()), 201
    else:
        return jsonify({'error': 'Missing name or price parameter'}), 400

# GET baked goods ordered by price
@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_serialized = [bg.to_dict() for bg in baked_goods]
    return jsonify(baked_goods_serialized), 200

# GET the most expensive baked good
@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return jsonify(most_expensive.to_dict() if most_expensive else {}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
from flask import Blueprint, request, jsonify
from models import Dish, DishIngredient, db

dishes_bp = Blueprint('dishes', __name__)


@dishes_bp.route('', methods=['GET'])
def list_dishes():
    category = request.args.get('category')
    cuisine = request.args.get('cuisine')
    search = request.args.get('search')

    query = Dish.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if cuisine:
        query = query.filter_by(cuisine=cuisine)
    if search:
        query = query.filter(Dish.name.ilike(f'%{search}%'))

    dishes = query.all()
    return jsonify([d.to_dict() for d in dishes])


@dishes_bp.route('/<int:dish_id>', methods=['GET'])
def get_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    data = dish.to_dict()
    data['ingredients'] = [di.to_dict() for di in DishIngredient.query.filter_by(dish_id=dish_id).all()]
    return jsonify(data)


@dishes_bp.route('/ingredients', methods=['POST'])
def get_ingredients():
    data = request.get_json()
    dish_ids = data.get('dish_ids', [])
    if not dish_ids:
        return jsonify([])

    ingredients = DishIngredient.query.filter(DishIngredient.dish_id.in_(dish_ids)).all()
    result = {}
    for di in ingredients:
        if di.ingredient:
            key = di.ingredient.name
            if key not in result:
                result[key] = {
                    'name': di.ingredient.name,
                    'unit': di.ingredient.unit,
                    'quantity': di.quantity,
                    'is_mandatory': di.ingredient.is_mandatory
                }
    return jsonify(list(result.values()))

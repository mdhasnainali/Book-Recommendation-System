from flask import Flask, jsonify
from flask_restful import Resource, Api
from process_result import get_similar_books, get_homepage, build_model


app = Flask(__name__)
api = Api(app)


class ContentBasedBookRecommendation(Resource):

    def get(self, book_id):
        result = get_similar_books(book_id)
        data = {
            "book_id": book_id,
            "recommended_books": result
        }
        return jsonify(data)


class CollaborativeFilteringBasedBookRecommendation(Resource):

    def get(self, user_id):
        result = get_homepage(user_id)
        data = {
            "user_id": user_id,
            "recommended_books": result
        }
        return jsonify(data)


class BuildTheModel(Resource):

    def get(self):
        build_model()
        data = {
            "message": "The model is executing.."
        }
        return jsonify(data)


api.add_resource(ContentBasedBookRecommendation,
                 '/similar_books/<int:book_id>')
api.add_resource(CollaborativeFilteringBasedBookRecommendation,
                 '/homepage/<int:user_id>')
api.add_resource(BuildTheModel,
                 '/build_model')


# driver function
if __name__ == '__main__':

    app.run(debug=True)

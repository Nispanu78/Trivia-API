import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# handles pagination of questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

 # function to create and configure the app
def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

# CORS is set up so that it allows all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
      'Content-Type, Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
      'GET,PUT,POST,DELETE,OPTIONS')

      return response
    @app.route('/categories')
    def obtain_categories():
      # gets all categories and add them to a dictionary
      categories = Category.query.all()
      categories_dict = {}
      for category in categories:
          categories_dict[category.id] = category.type
# abort 404 is shown if no category is found
          if (len(categories_dict) == 0):
            abort(404)
            return jsonify({
                'success': True,
                'categories': categories_dict
        })

# handles get requests for showing questions
    @app.route('/questions')
    def get_questions():
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      categories = list(map(Category.format, Category.query.all()))

# abort 404 is shown if no question is found
      if len(current_questions) == 0:
          abort(404)

# jsonify is used to return the data to be shown
          return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories,
            'current_category': None,

        })

# handles DELETE questions by using a question ID
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
      try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

# abort 404 if no question is found
            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

# jsonify returns successful deletion of question
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

      except:
            abort(422)

# handles post requests to load data from body and create new questions
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question,answer=new_answer,
            difficulty=new_difficulty, category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

# jsonify is used to return the data to be shown
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

# finds questions based on a search of terms
    @app.route('/questions/<searchTerm>', methods=['POST'])
    def search_questions(searchTerm):
        questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
        paginated_questions = paginate_questions(request,questions)

# 404 if no question is found
        if len(paginated_questions) == 0:
            abort(404)

# jsonify is used to return the data to be shown
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': ''
        })

# handles questions based on categories
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 for bad request if category isn't found
        if (category is None):
            abort(400)

        selection = Question.query.filter_by(category=category.id).all()
        paginated_questions = paginate_questions(request, selection)

# jsonify is used to return the data to be shown
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

# handles questions retrieved to play the quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

# Retrieve questions have not been answered yet by referring to their specific category
        try:
            if quiz_category['id'] == 0:
                selection = Question.query.filter(
                        Question.id.notin_((previous_questions))).all()
                total_questions = Question.query.all()
            else:
                selection = Question.query.filter(
                    Question.category==quiz_category['id']).filter(
                        Question.id.notin_((previous_questions))).all()
                total_questions = Question.query.filter(
                    Question.category==quiz_category['id']).all()

            if len(previous_questions) == len(total_questions):
                return jsonify({
                    "success": True,
                    "question": None
                })

# finds new random question from the selection
            new_question = selection[random.randrange(0, len(selection))]

# jsonify is used to return a new question
            return jsonify({
                "success": True,
                "question": new_question.format()
            })
        except:
            abort(422)


# error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
      }), 405
    return app

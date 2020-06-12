import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

     def test_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])

    def test_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_invalid_page(self):
        response = self.client().get('questions?page=2000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_delete_question(self):
        question_id = 1
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)
        if response.status_code == 404:
            self.assertEqual(data['success'], False)
        else:
            self.assertEqual(data['deleted'], 1)

    def test_delete_question_fail(self):
        response = self.client().delete('questions/100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_add_question(self):
        questions_before_new_question_add = len(Question.query.all())
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['total_questions'], questions_before_new_question_add + 1)

    def test_400_add_question(self):
        questions_before_new_question_add = len(Question.query.all())
        response = self.client().post('/questions', json=self.new_question_fail)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad request')
        self.assertEqual(questions_before_new_question_add, len(Question.query.all()))

    def test_search_question(self):
        response = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Sports')

    def test_404_get_questions_by_category(self):
        response = self.client().get('/categories/508/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_random_questions(self):
        response = self.client().post('/quizzes',
                                 json={
                                     'previous_questions': [6],
                                     'quiz_category': {'type': 'Entertainment',
                                                       'id': '5'}
                                 })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 5)
        self.assertNotEqual(data['question']['id'], 6)
        self.assertTrue(data['question'])

    def test_400_get_random_questions(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

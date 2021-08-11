import os
from re import I
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
        self.database_name = "trivia"
        self.database_path = "postgresql://{}/{}".format('postgres:123@localhost:5434', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['categories']))
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        test_questions = Question.query.order_by(Question.id).limit(10).all()
        tst = [q.format() for q in test_questions]
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['questions'],tst)
        self.assertEqual(data['totalQuestions'],Question.query.count())
        self.assertTrue(len(data['categories']))
        self.assertFalse(data['currentCategory'])

    def test_delete_404(self):
        res = self.client().delete('/questions/100000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'not found')
        self.assertFalse(data['success'])

    def test_delete_200(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])

    def test_questions_for_category_doesnt_exist_404(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'not found')
        self.assertFalse(data['success'])
    
    def test_questions_for_category_200(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        tst = Question.query.filter_by(category="1").all()
        tst_q = [q.format() for q in tst[:10]]

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['questions'],tst_q)
        self.assertEqual(data['totalQuestions'],len(tst))
        self.assertFalse(data['currentCategory'])

    def test_add_question_200(self):
        new_question = {
            'question':'test_question',
            'answer':'test_answer',
            'difficulty':1,
            'category':'1'
        }
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])

    def test_add_question_400(self):
        new_question = {
            'new_question':'test'
        }
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['message'],'bad request')
    
    def test_search(self):
        query = {'searchTerm':"country"}
        res = self.client().post('/questions',json=query)
        data = json.loads(res.data)

        expected = Question.query.filter(Question.question.ilike(f"%country%")).all()
        questions = [q.format() for q in expected[:10]]
        
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success']) 
        self.assertEqual(data['questions'],questions)
        self.assertEqual(data['totalQuestions'],len(expected))        
        self.assertFalse(data['currentCategory'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
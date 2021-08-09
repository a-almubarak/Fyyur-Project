import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from werkzeug.exceptions import RequestEntityTooLarge

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','POST,GET,PATCH,DELETE')
    return response

  def get_cats():
    cats = Category.query.all()
    data = [cat.format() for cat in cats]
    return data
  
  nbQuestions = 10
  def paginated_questions(request,selection):
    page = request.args.get('page',1,type=int)
    start = (page-1)*nbQuestions
    end = start + nbQuestions
    questions = selection
    data = [question.format() for question in questions]
    return data[start:end]
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    cats = get_cats()
    return jsonify({
      'categories':cats
    })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def get_question():
    data = Question.query.all()
    questions = paginated_questions(request,data)
    return jsonify({
      'questions':questions,
      'totalQuestions':len(data),
      'categories':get_cats(),
      'currentCategory':None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>',methods=['DELETE'])
  def delete_question(q_id):
    question = Question.query.get(q_id)
    if not question:
      abort(404)
    question.delete()
    #check what to return if success
    return jsonify({
      'success':True
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  #needs review
  #no need for try..catch for searchTerm
  @app.route('/questions',methods=['POST'])
  def post_question():
    req = request.get_json()
    if 'question' in req or 'answer' in req or 'difficulty' in req or 'category' in req:
      question = req.get('question',None)
      answer = req.get('answer',None)
      difficulty = req.get('difficulty',None)
      category = req.get('category',None)
      try:
        q = Question(question=question,answer=answer,difficulty=difficulty,category=category)
        q.insert()
      except:
        abort(422)
    elif 'searchTerm' in req:
      search_term= req['searchTerm']
      try:
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
        qs = paginated_questions(request,selection)
        return jsonify({
          'questions':qs,
          'totalQuestions':len(selection.all()),
          'currentCategory':None
        })
      except:
        abort(422)
    else:
      abort(400)  


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #done
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def questions_for_cateogorie(cat_id):
    category = Category.query.get(cat_id)
    if not category:
      abort(404)
    else:
      selection = Question.query.filter_by(category=cat_id)
      #what if there's no questions ?
      qs = paginated_questions(request,selection)
      return jsonify({
        'questions':qs,
        'totalQuestions':len(selection.all()),
        'currentCategory':None
      })
    

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    
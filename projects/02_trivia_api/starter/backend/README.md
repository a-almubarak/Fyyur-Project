# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Endpoint documentation
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{
    'categories':{'1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports"}
}
```
```
GET '/questions?page=${integer}'
- Fetches a paginated set of questions, all of their categories, and total number of questions.
- Request Arguments: page - integer.
- Returns: An object with 10 paginated questions, total questions, object with all categories and string contain the current category.
{
    'questions':[{
        'id':1,
        'question':'this is questions',
        'answer':'an answer',
        'difficulty':3,
        'category':3
    }],
    'totalQuestions':18,
    'categories':{
        '1':'Science',
        '2':'History',
        ...
    },
    'currentCategory':'Science'
} 
```
```
DELETE '/questions/${id}'
- Delete the question with the given id.
- Request Argument: id - integer.
- Returns: No data besides HTTP Status Code.
```
```
GET '/categories/${id}/questions
- Fetches questions for a category given the id of the category.
- Request Argument: id - integer.
- Returns: An object with 10 paginated questions for the given category, total number of questions and the current category.
{
    'questions':[{
        'id':2,
        'questions':'a questions',
        'answer':'an answer',
        'difficulty':2,
        'category':3
    }],
    'totalQuestions':19,
    'currentCategory':'Science'
}
```
```
POST '/quizzes'
- Sends a post request to get the next question.
- Request Argument:
{
    'previous_questions': an array of question ids such as[1,2,3],
    'quiz_category':a string of the current category.
}
- Returns: An object with question details.
{
    'id':1,
    'questions':'Question',
    'answer':'Answer',
    'difficulty':4,
    'category':3
}
```
```
post '/questions'
- Send Post request to search for questions that contains a given term.
- Request Argument: 
{
    'searchTerm':'a search term'
}
- Returns: An object that contains an array of questions that contains the search term, the total number of questions that contains the term and the current category.
{
    'questions':[{
        'id':1,
        'question':'a question',
        'answer':'an answer',
        'difficulty':2,
        'category':4
    }]
    'totalQuestions':13,
    'currentCategory':'History
}
```

```
post '/questions'
- Send Post request to add a new question.
- Request Argument: 
{
    'question':'this is question',
    'answer':'this is answer',
    'difficulty':4,
    'category':5
}
- Returns: Does not return any new data.
```
## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

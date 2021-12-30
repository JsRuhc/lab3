**Lab 3**: ORM的学习与使用
=================================================

**orm.py**

.. code:: py

   # Software Architecture and Design Patterns -- Lab 3 starter code
   # Copyright (C) 2021 Hui Lan

   import model

   from sqlalchemy import create_engine
   from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
   from sqlalchemy.orm import mapper, relationship, sessionmaker, clear_mappers

   metadata = MetaData()

   articles = Table(
       'articles',
       metadata,
       Column('article_id', Integer, primary_key=True, autoincrement=True),
       Column('text', String(10000)),
       Column('source', String(100)),
       Column('date', String(10)),
       Column('level', Integer, nullable=False),
       Column('question', String(1000)),
       )


   users = Table(
       'users',
       metadata,
       Column('username', String(100), primary_key=True),
       Column('password', String(64)),
       Column('start_date', String(10), nullable=False),
       Column('expiry_date', String(10), nullable=False),
       )

   newwords = Table(
       'newwords',
       metadata,
       Column('word_id', Integer, primary_key=True, autoincrement=True),
       Column('username', String(100), ForeignKey('users.username')),
       Column('word', String(20)),
       Column('date', String(10)),
       )

   readings = Table(
       'readings',
       metadata,
       Column('id', Integer, primary_key=True, autoincrement=True),
       Column('username', String(100), ForeignKey('users.username')),
       Column('article_id', Integer, ForeignKey('articles.article_id')),
       )

   # map model's classes to database tables
   def start_mappers():
       metadata.create_all(create_engine('sqlite:///EnglishPalDatabase.db'))
       mapper(model.User, users)
       mapper(model.NewWord, newwords)
       mapper(model.Article, articles)
       mapper(model.Reading, readings)

**services.py**

.. code:: py

   # Software Architecture and Design Patterns -- Lab 3 starter code
   # An implementation of the Service Layer
   # Copyright (C) 2021 Hui Lan

   # word and its difficulty level
   WORD_DIFFICULTY_LEVEL = {'starbucks':5, 'luckin':4, 'secondcup':4, 'costa':3, 'timhortons':3, 'frappuccino':6}

   import pytest
   import math
   import model

   # two custom exception classes
   class UnknownUser(Exception):
       pass

   class NoArticleMatched(Exception):
       pass

   def read(user, user_repo, article_repo, session):
       # search user in database
       u = user_repo.get(user.username)

       # if the user doesn't exist or the pwd error, throw an UnknownUser Exception
       if u == None or u.password != user.password:
           raise UnknownUser()

       # search all articles in database
       articles = article_repo.list()

       # if no article in database, throw a NoArticleMatched Exception
       if articles == None:
           raise NoArticleMatched()

       # search user's new words in database
       words = session.execute(
           'SELECT word FROM newwords WHERE username=:username',
           dict(username=user.username),
       )

       # calculate user's WORD_DIFFICULTY_LEVEL
       sum = 0
       count = 0
       for word in words:
           sum += WORD_DIFFICULTY_LEVEL[word[0]]
           count += 1

       if count == 0:
           count = 1

       average = round(sum / count) + 1
       if average < 3:
           average = 3

       # recommend articles to users based on WORD_DIFFICULTY_LEVEL
       for article in articles:
           if average == article.level:
               article_id = user.read_article(article)
               session.add(model.Reading(username = user.username, article_id = article_id))
               session.commit()
               return article_id

       raise NoArticleMatched()

.. figure:: https://gitee.com/id10t/orm/raw/master/Screenshot.jpeg
   :alt: 运行结果

   运行结果

Let’s look the ``test_services.py``, we can know that the functions’
title tell us what need to test:

.. code:: py

   # Software Architecture and Design Patterns -- Lab 3 starter code
   # Run this script using the following command: pytest -v -s test_services.py
   # Copyright (C) 2021 Hui Lan

   import pytest

   import model
   import repository
   import services

   @pytest.mark.usefixtures('prepare_data')
   def test_read_article_level4(get_session):
       session = get_session()
       article_repo = repository.ArticleRepository(session)
       user_repo = repository.UserRepository(session)

       username = 'mrlan'
       password = '12345'
       user = model.User(username=username, password=password)
       article_id = services.read(user, user_repo, article_repo, session)

       result = session.execute(
           'SELECT article_id FROM readings WHERE username=:username',
           dict(username=username),
       )

       lst = [r[0] for r in result]

       assert article_id == 2
       assert lst[0] == 2



   @pytest.mark.usefixtures('prepare_data')
   def test_read_article_level5(get_session):
       session = get_session()
       article_repo = repository.ArticleRepository(session)
       user_repo = repository.UserRepository(session)

       username = 'lanhui'
       password = 'Hard2Guess!'
       user = model.User(username=username, password=password)
       article_id = services.read(user, user_repo, article_repo, session)

       result = session.execute(
           'SELECT article_id FROM readings WHERE username=:username',
           dict(username=username),
       )

       lst = [r[0] for r in result]
       assert article_id == 1
       assert lst[0] == 1



   @pytest.mark.usefixtures('prepare_data')
   def test_read_article_level6(get_session):
       session = get_session()
       article_repo = repository.ArticleRepository(session)
       user_repo = repository.UserRepository(session)

       username = 'hui'
       password = 'G00d@English:)'
       user = model.User(username=username, password=password)
       with pytest.raises(services.NoArticleMatched):
           article_id = services.read(user, user_repo, article_repo, session)



   @pytest.mark.usefixtures('prepare_data')
   def test_user_with_wrong_password(get_session):
       session = get_session()
       article_repo = repository.ArticleRepository(session)
       user_repo = repository.UserRepository(session)

       username = 'mrlan'
       password = '54321'
       user = model.User(username=username, password=password)
       with pytest.raises(services.UnknownUser):
           article_id = services.read(user, user_repo, article_repo, session)



   @pytest.mark.usefixtures('prepare_data')
   def test_user_with_wrong_username(get_session):
       session = get_session()
       article_repo = repository.ArticleRepository(session)
       user_repo = repository.UserRepository(session)

       username = 'MrLan'
       password = '12345'
       user = model.User(username=username, password=password)
       with pytest.raises(services.UnknownUser):
           article_id = services.read(user, user_repo, article_repo, session)

The titles of the first three functions all tell us that it is a test
read article level, next we look at the content; First initialize the
user and article repositories, then created the entity user, call the
``read()`` function of the services to get the ``article_id``, finally,
the assertion comparison;

But the third function ``test_read_article_level6()`` is special,
because there are no article on level6 in database, so it need to throw
exceptions – ``NoArticleMatched()``;

And the last two functions are used to verify that the user exists, so
we need to search all users in database, and compares them, if no
exists, throw exceptions – ``UnknownUser()``;

``read()`` function follows the Single Responsibility Principle (SRP)
principle, because the function only used to return ``article_id``, if
no ``article_id``, then throw exceptions.

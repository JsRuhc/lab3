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

    #接受信息
    u = user_repo.get(user.username)
    
    # 判断用户密码是否正确
    if u == None or u.password != user.password:
        raise UnknownUser()

    # 搜索 用户表中的 生词
    words = session.execute(
        'SELECT word FROM newwords WHERE username=:username',
        dict(username=user.username),
    )

    # 计算用户生词水平
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

    
    # 获取文章
    articles = article_repo.list()
    if articles == None:
        raise NoArticleMatched()


    
    # 根据用户生词水平推荐文章
    for article in articles:
        if average == article.level:
            article_id  = user.read_article(article)
            session.add(model.Reading(username = user.username, article_id = article_id))
            session.commit()
            return article_id

    raise NoArticleMatched()




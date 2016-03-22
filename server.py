from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func,desc
from models import *
from utils import *
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class PostConfig:
    """
    Class used by get_posts, and get_table_posts
    to get the specific posts (as filtered)
    """
    def reset():
        PostConfig.startdate = datetime.strptime('01012000','%m%d%Y')
        PostConfig.enddate = datetime.now()
        PostConfig.limit = 500
        PostConfig.tags = None

    def get():
        return db.session.query(Post).filter(
            Post.time.between(PostConfig.startdate, PostConfig.enddate)
            ).limit(PostConfig.limit).all()


class CommentConfig:
    """
    Class used by get_comments,
    to get the specific comments (as filtered)
    """
    def reset():
        CommentConfig.startdate = datetime.strptime('01012000', '%m%d%Y')
        CommentConfig.enddate = datetime.now()
        CommentConfig.limit = 500

    def get():
        return db.session.query(Comment).filter(
            Post.time.between(CommentConfig.startdate, CommentConfig.enddate)
            ).limit(CommentConfig.limit).all()

PostConfig.reset()
CommentConfig.reset()


@app.route('/')
def home():
    """
    Serves the main page
    """
    f = open("index.html")
    return f.read()



#######################################
#  
#           GETTING METADATA
#
#########################################

@app.route('/get/info')
def info():
    data = dict()
    data['course'] = "Computer Science 70"
    data['numviews'] = 400
    data['numposts'] = 23
    data['timetill'] = 10
    return jsonify(data=data)


@app.route('/get/popular_keywords')
def popular_keywords():
    keywords = db.session.query(Keyword,func.count(keyword_table.c.post).label('total')).join(keyword_table).group_by(Keyword).order_by('total DESC').limit(5).all()
    keywords = [[k[0].name.title(), k[1]] for k in keywords]
    return jsonify(data=keywords)

@app.route('/get/popular_posts')
def popular_posts():
    popular = dict()
    last_week = datetime.now() - timedelta(weeks=1)
    most_viewed = db.session.query(Post).filter(Post.time > last_week).order_by(Post.views.desc()).first()
    if most_viewed is not None: 
        popular['views'] = post_to_dictionary(most_viewed)
    most_commented_id = db.session.query(Comment.post_id,func.count(Comment.index).label('num')).filter(Comment.time > last_week).group_by(Comment.post_id).order_by(desc('num')).first()[0]
    most_commented = db.session.query(Post).get(most_commented_id)
    if most_commented is not None:
        popular['comments'] = post_to_dictionary(most_commented)
    most_recent = db.session.query(Post).order_by(Post.time.desc()).limit(5).all()
    popular['recent'] = [post_to_dictionary(p) for p in most_recent]
    return jsonify(data=popular)


########################################
#
#           GETTING POSTS
#
########################################

@app.route('/get/post')
def get_posts():
    posts = PostConfig.get()
    postdata = [post_to_dictionary(post) for post in posts]
    return jsonify(data=postdata)


@app.route('/get/post_table')
def get_post_table():
    posts = PostConfig.get()
    postdata = [post_to_table(post) for post in posts]
    return jsonify(data=postdata)


@app.route('/get/comments')
def get_comments():
    comments = CommentConfig.get()
    commentdata = [comment_to_dictionary(comment) for comment in comments]
    return jsonify(data=commentdata)


@app.route('/get/tags')
def get_tags():
    tags = db.session.query(Tag).all()
    return jsonify(data=[tag.name for tag in tags])


@app.route('/get/post/<int:post_id>')
def get_post(post_id):
    post_id = to_default(post_id)
    post = db.session.query(Post).get(post_id)
    dictionary = post_to_dictionary(post)
    return jsonify(data=dictionary)

########################################
#
#           FILTER RESULTS
#
########################################


@app.route('/select/post')
def select_post():
    startdate = request.args.get('start',None)
    if startdate:
        PostConfig.startdate = datetime.strptime(startdate, '%m%d%Y')
        print("Updating start date to ", startdate)

    enddate = request.args.get('end',None)
    if enddate:
        PostConfig.enddate = datetime.strptime(enddate,'%m%d%Y')
        print("Updating end date to ", enddate)

    return ''


@app.route('/select/tag')
def select_tag():
    tag = request.args.get('tag',None)
    if tag:
        PostConfig.tags = tag


@app.route('/select/comment')
def select_comment():
    startdate = request.args.get('start',None)
    if startdate:
        CommentConfig.startdate = datetime.strptime(startdate, '%m%d%Y')
        print("Updating start date to ", startdate)
    enddate = request.args.get('end',None)
    if enddate:
        CommentConfig.enddate = datetime.strptime(enddate,'%m%d%Y')
        print("Updating end date to ", enddate)

    return ''

@app.route('/select/reset')
def reset():
    PostConfig.reset()
    CommentConfig.reset()
    return ''

################################
#
#       MAIN
#
################################


if __name__ == '__main__':
    app.debug = True
    app.run()

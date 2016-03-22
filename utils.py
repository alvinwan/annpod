import time
from datetime import datetime
from textblob import TextBlob


def post_to_dictionary(post):
    """
    Converts a post into a JSON-transferrable dictionary of relevant info
    and analyses. Currently, contains the following items:
        title - The title of the submission
        body   - The text of the ubmission
        tags    - The tags on the post 
        date    - DateTime Object when the comment was submitted
        time    - The time when the comment was submitted (epoch time)
        polarity- TextBlob's guess of the polarity of the comment
        subjectivity- Textblob's guess of subjectivity of comment.
    """

    p = dict()
    p['title'] = post.title
    p['body'] = post.text
    p['tags'] = [tag.name for tag in post.tags]
    p['date'] = post.time
    p['time'] = time.mktime(post.time.timetuple())
    if post.analysis:
        p['polarity'] = post.analysis[0].polarity
        p['subjectivity'] = post.analysis[0].subjectivity
        p['keywords'] = [kw.name for kw in post.analysis[0].keywords]
    p['views'] = post.views
    p['favorites'] = post.favorites
    p['comments'] = [comment_to_dictionary(comm) for comm in post.comments]
    p['index'] = post.index
    return p


def post_to_table(post):
    """
    Converts a post into a list of relevant info
    and analyses (to be placed in table format):
    """
    p = list()
    p.append(post.index)  # Index
    p.append(post.title)  # Title
    p.append("--".join([tag.name for tag in post.tags]))  # Categories
    p.append(datetime.strftime(post.time,'%m/%d/%Y'))  # Time
    p.append(len(post.comments))
    return p


def comment_to_dictionary(comment):
    """
    Converts a comment into a JSON-transferrable dictonary of relevant
    info and analysis: Currently, contains the following items:
        comment - The text of the comment
        time    - The time when the comment was submitted
        polarity- TextBlob's guess of the polarity of the comment
        subjectivity- Textblob's guess of subjectivity of comment.
    """
    p = dict()
    p['comment'] = comment.text
    p['date'] = comment.time
    p['time'] = time.mktime(comment.time.timetuple())
    p['type'] = comment.type
    return p


to_default = lambda x: max(1, x)
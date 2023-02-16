from main.models import Category, Status

def category_query():
    return Category.query

def status_query():
    return Status.query

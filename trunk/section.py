import os

from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Section(db.Model):
    path = db.StringProperty()
    parent_path = db.StringProperty()
    title = db.StringProperty()
    
    def __str__(self):
        path = os.path.join(os.path.dirname(__file__), 'blank.html')
        return template.render(path, {'title': self.title, 'body': '<h1>Coming Soon</h1>'})

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(path):
    return Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path))[0]

def create_section(path, parent_path, title):
    section = Section(parent=section_key(path), path=path, parent_path=parent_path, title=title)
    section.put()
    return section
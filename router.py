from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import section

class Router(webapp.RequestHandler):
    def get(self, path):
        try:
            self.response.out.write(section.get_section(path))
        except:
            if(path == '/'):
                self.response.out.write(section.create_section(path='/', parent_path=None, title='Welcome to GAE-CMS'))
            else:
                self.error(404)

application = webapp.WSGIApplication([('(/.*)', Router)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
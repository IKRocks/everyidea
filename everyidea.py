#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]

class Page(webapp2.RequestHandler):
    def templateValues(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        return {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }

class Home(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/index.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class Login(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/login.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class Reading(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/reading.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class News(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/news.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class Experiments(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/experiments.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class Brainstorming(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/brainstorming.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))

class Fundraising(Page):
    def get(self):
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/header.html').render(self.templateValues()))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/fundraising.html').render({}))
        self.response.write(JINJA_ENVIRONMENT.get_template('pages/footer.html').render({}))


class Guestbook(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('guestbook.html')
        self.response.write(template.render(template_values))

class SignGuestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/guestbook?' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/login', Login),
    ('/reading', Reading),
    ('/news', News),
    ('/experiments', Experiments),
    ('/brainstorming', Brainstorming),
    ('/fundraising', Fundraising),
    ('/guestbook', Guestbook),
    ('/sign', SignGuestbook),
], debug=True)

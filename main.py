#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def get_posts(limit, offset):
    return db.GqlQuery("select * from Posts order by created desc limit %s offset %s" % (limit, offset))


class MainHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))


    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class Blog(MainHandler):
    def get(self):
        page = self.request.get('page')
        if page:
            page = int(page)
            posts = get_posts(5, page*5)
            previous = page - 1
            if posts.count() - (page+1) *5 > 0:
                next = page+1

            else:
                next = False



        else:
            page = 0
            posts = get_posts(5, page)
            next = 1
            previous = False

        self.render('blog.html', posts=posts, next=next, previous=previous)

class NewPost(MainHandler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        body = self.request.get('body')

        if subject and body:
            p = Posts(subject=subject, body=body)
            p.put()
            id = str(p.key().id())

            self.redirect('/blog/' + id)

        else:
            error = 'You need to have both a subject and body'
            self.render('newpost.html', subject=subject, body=body, error=error)

class ViewPerma(MainHandler):
    def get(self, id):
        id = int(id)
        if Posts.get_by_id(id):
            p = Posts.get_by_id(id)
            self.render('post.html', p=p)
        else:
            self.write("That posts doesn't exist")




class Posts(db.Model):
    subject = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)








app = webapp2.WSGIApplication([
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPerma),
    ('/blog/newpost', NewPost),

], debug=True)

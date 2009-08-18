#!/usr/bin/env python
#
# Instalicious - push Delicious bookmarks to Instapaper.
 
# To run periodically - "crontab -e", then add the line:
# 30 * * * * /path/to/instalicious.py > /dev/null
#
# If you're using Python < 2.6 ("python --version"), you will need to install
# simplejson (e.g. "easy_install simplejson")
#
# Copyright (c) 2009 Michael Mahemoff Released under MIT open source License -
# see http://www.opensource.org/licenses/mit-license.php
#
# There are problems here due to unicode encoding - see
# http://psf.upfronthosting.co.za/roundup/tracker/issue1712522

##############################################################################
# Config
##############################################################################

toread_tag='toread'
instaliciousd_tag='instaliciousd'

delicious_username='mahemoff'
delicious_password='hard2guess'

instapaper_username='michael@mahemoff.com'
instapaper_password='hard2guess'

##############################################################################
# No need to change anything below here
##############################################################################

import httplib, urllib, urllib2, sys
try:
  import simplejson as json # version < 2.6
except ImportError:
  import json

reload(sys)
sys.setdefaultencoding('utf_8')

def download_delicious_bookmarks(delicious_username, toread_tag):
  bookmarks_url = "http://feeds.delicious.com/v2/json/" + delicious_username + "/" + toread_tag
  bookmarks_json = urllib2.urlopen(bookmarks_url).read()
  print bookmarks_json
  return json.loads(bookmarks_json)

def add_to_instapaper(url, instapaper_username, instapaper_password):
  params = urllib.urlencode(
    {'username': instapaper_username,
     'password': instapaper_password,
     'url': url,
     'auto-title': '1'
    }
  )
  headers = {"Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"}
  conn = httplib.HTTPConnection("www.instapaper.com")
  conn.request("POST", "/api/add", params, headers)
  response = conn.getresponse()
  print url, response.status, response.reason

def untag_from_delicious(bookmark, toread_tag, instaliciousd_tag, delicious_username, delicious_password):
  altered_tag_index = bookmark["t"].index(urllib.quote(toread_tag))
  bookmark["t"][altered_tag_index] = instaliciousd_tag
  for key in ["u","d","n"]:
    if isinstance(bookmark[key], unicode):
      bookmark[key] = bookmark[key].encode('utf-8')
  # print "4" + bookmark["t"]
  add_url = "https://api.del.icio.us/v1/posts/add?url=%s&description=%s&extended=%s&tags=%s&replace=yes" % (urllib.quote(bookmark["u"]), urllib.quote(bookmark["d"]), urllib.quote(bookmark["n"]), "+".join(bookmark["t"]))
  _auth_call(add_url, delicious_username, delicious_password)

def _auth_call(url, auth_username, auth_password):
  passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
  passman.add_password(None,url,auth_username,auth_password)
  authhandler = urllib2.HTTPBasicAuthHandler(passman)
  opener = urllib2.build_opener(authhandler)
  urllib2.install_opener(opener)
  return urllib2.urlopen(url).read()

for bookmark in download_delicious_bookmarks(delicious_username, toread_tag):
  add_to_instapaper(bookmark["u"], instapaper_username, instapaper_password)
  untag_from_delicious(bookmark, toread_tag, instaliciousd_tag, delicious_username, delicious_password)

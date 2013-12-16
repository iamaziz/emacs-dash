import sqlite3
import os
import urllib2
from bs4 import BeautifulSoup as bs
import requests


root_url = 'http://www.gnu.org/software/emacs/manual/html_node/emacs/'
output = 'emacs.docset/Contents/Resources/Documents'
docpath = output + '/'
if not os.path.exists(docpath): os.makedirs(docpath)

data = requests.get(root_url).text
soup = bs(data)
open(os.path.join(output, 'index.html'), 'wb').write(data.encode('ascii', 'ignore'))

def update_db(name, path):
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'func', path))
    print 'DB add >> name: %s, path: %s' % (name, path)


"""
Scan all links in a given root url then download the page of each link and update database.
"""


def add_docs():
    for i, link in enumerate(soup.findAll('a')):
        name = link.text.strip()
        path = link.attrs['href'].strip()

        print "%s: " % i,

        if path.startswith("/"): path = path[1:]

        # figure out directories and create them
        if "/" in path and not "https://" in path and not "http://" in path:

            subdir = path
            folder = os.path.join(docpath)

            # split subdirs
            for i in range(len(subdir.split("/")) - 1):
                folder += subdir.split("/")[i] + "/"

            # add a directory for sub-folder(s)
            if not os.path.exists(folder): os.makedirs(folder)

        print path,

        # download docs and update db
        try:
            print " V"
            if name and path:
                update_db(name, path)

            path = path.split('#')[-2]
            url = root_url + path
            res = urllib2.urlopen(url)
            doc = open(docpath + path, 'wb')
            doc.write(res.read())
            doc.close()
            print "doc: ", path

        except:
            print " X"
            pass


if __name__ == '__main__':

    db = sqlite3.connect('emacs.docset/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # start
    add_docs()

    # commit and close db
    db.commit()
    db.close()
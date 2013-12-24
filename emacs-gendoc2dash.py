"""
    Generate Dash docset for the Emacs Editor
    http://www.gnu.org/software/emacs/manual/html_node/emacs/
"""
import sqlite3
import os
import urllib
import urllib2
from bs4 import BeautifulSoup as bs
import requests


# docset info
docset_name = 'Emacs.docset'
root_url = 'http://www.gnu.org/software/emacs/manual/html_node/emacs/'
output = docset_name + '/Contents/Resources/Documents'

# create directory
docpath = output + '/'
if not os.path.exists(docpath): os.makedirs(docpath)
icon = 'http://semantic.supelec.fr/popineau/images/carbon-emacs-icon.png'

# soup
data = requests.get(root_url).text    # for online page
soup = bs(data)
index = str(soup.find(id='main'))
open(os.path.join(output, 'index.html'), 'wb').write(index)
# add icon
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, path):
    typ = 'func'
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
    print 'DB add >> name: %s, path: %s' % (name, path)


def add_docs():
    for i, link in enumerate(soup.findAll('a')):
        name = link.text.strip()
        path = link.get('href')

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


def add_infoplist():
    name = docset_name.split('.')[0]
    info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
           "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
           "<plist version=\"1.0\"> " \
           "<dict> " \
           "    <key>CFBundleIdentifier</key> " \
           "    <string>{0}</string> " \
           "    <key>CFBundleName</key> " \
           "    <string>{1}</string>" \
           "    <key>DocSetPlatformFamily</key>" \
           "    <string>{2}</string>" \
           "    <key>isDashDocset</key>" \
           "    <true/>" \
           "    <key>dashIndexFilePath</key>" \
           "    <string>index.html</string>" \
           "</dict>" \
           "</plist>".format(name, name, name)
    open(docset_name + '/Contents/info.plist', 'wb').write(info)


if __name__ == '__main__':

    db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # start
    add_docs()
    add_infoplist()

    # commit and close db
    db.commit()
    db.close()
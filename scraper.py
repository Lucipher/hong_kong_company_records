# coding=utf-8

import scraperwiki
import lxml.html           
from time import sleep
from thready import threaded
import dataset

import logging
logging.basicConfig()

import os
from hashlib import sha1


# a directory for caching files we've already downloaded
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')

def url_to_filename(url):
    """ Make a URL into a file name, using SHA1 hashes. """

    # use a sha1 hash to convert the url into a unique filename
    hash_file = sha1(url).hexdigest() + '.html'
    return os.path.join(CACHE_DIR, hash_file)


def store_local(url, content):
    """ Save a local copy of the file. """

    # If the cache directory does not exist, make one.
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Save to disk.
    local_path = url_to_filename(url)
    with open(local_path, 'wb') as f:
        f.write(content)


def load_local(url):
    """ Read a local copy of a URL. """
    local_path = url_to_filename(url)
    if not os.path.exists(local_path):
        return None

    with open(local_path, 'rb') as f:
        return f.read()

db = dataset.connect('sqlite:///scraperwiki.sqlite')

maxcr = 2120960
mincr = 1686538

def scrape(crno):
    crnostr = "%07d" % crno
    baseurl = "https://www.mobile-cr.gov.hk/mob/cps_criteria.do?queryCRNO="
    url = baseurl + crnostr

    print "trying local", crnostr
    html = load_local(url)
    if html is None:
        print "trying site", crnostr
        html = scraperwiki.scrape(url).decode('utf-8')
        print "storing local", crnostr
        store_local(url, html.encode('utf-8'))
    else:
        html = html.decode('utf-8')

    if '沒有紀錄與輸入的查詢資料相符' in html.encode('utf-8'):
        print 'NO MATCHING RECORD FOUND FOR THE SEARCH INFORMATION INPUT!'
        return nil
    root = lxml.html.fromstring(html) # , encoding="utf-8")
    tds = root.cssselect("tr td tr td")
    namestds = root.cssselect("td.data")   

    while tds == []:
        print "trying", crnostr, "again"
        sleep(46)
        html = scraperwiki.scrape(baseurl + crnostr).decode('utf-8')
        root = lxml.html.fromstring(html) # , encoding="utf-8")
        tds = root.cssselect("tr td tr td")
        namestds = root.cssselect("td.data")   

        #for idx, val in enumerate(tds):
        #    print idx, ":", val.text_content().encode('utf-8')
    names = {}
    for nameidx, nameval in enumerate(namestds):
        names["Name" + str(nameidx)] = nameval.text_content()[10:]
        names["Name" + str(nameidx) + "date"] = nameval.text_content()[:10]

    print "got", tds[1].text_content() 

    data = {
        'cr' : tds[1].text_content(),
        'English Company Name' : tds[2].text_content().rsplit('\r')[1].lstrip('\n\t'),
        'Chinese Company Name' : tds[2].text_content().rpartition('\r')[2].lstrip('\r\n\t'),
        'Company Type' : tds[4].text_content()[:-1],
        'Date of incorporation' : tds[6].text_content(),
        # 'Company status' : tds[8].text_content()[:-1],
        'Active status' : tds[8].text_content()[:-1],
        'Remarks' : tds[9].text_content().replace(u"備註：",""),
        'Winding up mode' : tds[11].text_content()[:-1],
        'Date of Dissolution' : tds[13].text_content(),
        'Register of Charges' : tds[15].text_content()[:-1],
        'Important Note' : tds[16].text_content().replace(u"重要事項：","").lstrip('\r\n\t')
    }
    data.update(names)
    
    db['swdata'].upsert(data, ['cr'])
    print "wrote", tds[1].text_content()

threaded(range(mincr, maxcr), scrape, num_threads = 20)

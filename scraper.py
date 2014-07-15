import scraperwiki

# max 1891157
for crno in range(1, 10):
    crnostr = "%07d" % crno
    baseurl = "https://www.mobile-cr.gov.hk/mob/cps_criteria.do?queryCRNO="
    scraperwiki.scrape("https://www.mobile-cr.gov.hk/mob/locale_us.jsp") # English!
    html = scraperwiki.scrape(baseurl + crnostr).decode('utf-8')

    import lxml.html           
    root = lxml.html.fromstring(html) # , encoding="utf-8")

    tds = root.cssselect("tr td tr td")
    namestds = root.cssselect("td.data")   

    if tds == []:
        pass
    else:
        for idx, val in enumerate(tds):
            print idx, ":", val.text_content().encode('utf-8')
        print tds[2].text_content().encode('utf-8')
        names = {}
        for namesno in range(len(namestds)):
            names["Name" + str(namesno)] = namestds[namesno].text_content().encode('utf-8').to_s
        data = {
        'cr' : tds[1].text_content().encode('utf-8'),
        'English Company Name' : tds[2].text_content().encode('utf-8').rsplit('\r')[1].lstrip('\n\t').to_s,
        'Chinese Company Name' : tds[2].text_content().encode('utf-8').rpartition('\r')[2].lstrip('\r\n\t').to_s,
        'Company Type' : tds[4].text_content().encode('utf-8')[:-1].to_s,
        'Date of incorporation' : tds[6].text_content().encode('utf-8').to_s,
        # 'Company status' : tds[8].text_content().encode('utf-8')[:-1],
        'Active status' : tds[8].text_content().encode('utf-8')[:-1].to_s,
        'Remarks' : tds[9].text_content().encode('utf-8')[16:].to_s,
        'Winding up mode' : tds[11].text_content().encode('utf-8')[:-1].to_s,
        'Date of Dissolution' : tds[13].text_content().encode('utf-8').to_s,
        'Register of Charges' : tds[15].text_content().encode('utf-8')[:-1].to_s,
        'Important Note' : tds[16].text_content().encode('utf-8')[16:].lstrip('\r\n\t').to_s,
        'Name History' : names
        }
        

    scraperwiki.sqlite.save(unique_keys=['cr'], data=data)
        

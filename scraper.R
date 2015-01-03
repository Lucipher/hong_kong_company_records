library(parallel)
                                        #library(data.table)
library(rvest)
library(lubridate)
library(stringr)


deleteslashes <- function(x) {str_replace_all(x, "[\n\t\r]", "")}

extractnames <- function(names) {
        if (length(grep("-THE-", names)) == 1) {
            namesenglish <- str_extract(names, ".+-THE-")
        } else if (length(grep("-The-", names)) == 1) {
            namesenglish <- str_extract(names, ".+-The-")
        } else if (length(grep("Limited", names)) == 1) {
            namesenglish <- str_extract(names, ".+Limited")
        } else if (length(grep("LTD", names)) == 1) {
            namesenglish <- str_extract(names, ".+LTD")
        } else {
            namesenglish <- str_extract(names, ".+LIMITED")
        }
        nameschinese <- str_replace(names, fixed(namesenglish), "")

        return(list(deleteslashes(namesenglish), deleteslashes(nameschinese)))
}

scrape <- function(crno) {
    crnostr = sprintf("%07d", crno)
    baseurl = "https://www.mobile-cr.gov.hk/mob/cps_criteria.do?queryCRNO="
    url = paste0(baseurl, crnostr)

    print(c("trying", crnostr))
    html <- html(url, encoding = "utf-8")

    if (length(html_nodes(html, "img")) > 0) {
        print(c("sleeping, then trying again", crnostr))
#        save(scrapelist, file = "scrapelistlist.Rdata")
        Sys.sleep(50)
        html <- html(url, encoding = "utf-8")
    }
    
    if (!is.null(html_node(html, "body"))) {
        if (length(grep('沒有紀錄與輸入的查詢資料相符', html_text(html_node(html, "body"))) > 0)) {
            print('NO MATCHING RECORD FOUND FOR THE SEARCH INFORMATION INPUT!')
            return(list(crno = crno))
        }
    }

    tds <- html_text(html_nodes(html, "td:nth-child(2)"))

    crdata <- list(crno = tds[1], companytype = deleteslashes(tds[2]), incorporationdate = dmy(tds[3]), status = deleteslashes(tds[4]), windingupmode = deleteslashes(tds[5]), dissolutiondate = dmy(tds[6]), registeravailable = deleteslashes(tds[7]))
    
    companyname <- str_replace(deleteslashes(html_text(html_node(html, "td tr:nth-child(2) td"))), "公司名稱：", "")
    companynameextract <- extractnames(companyname)
    crdata[["currentnameenglish"]] = companynameextract[[1]]
    crdata[["currentnamechinese"]] = companynameextract[[2]]

    crdata[["remarks"]] = deleteslashes(html_text(html_node(html, ".sameasbody")))
    crdata[["note"]] = str_replace(html_text(html_node(html, "tr:nth-child(10) td")), fixed("重要事項：\r\n\t\t\t\t\t"), "")
    
    names <- html_nodes(html, ".data")
    for (name in 1:length(names)) {
        tempname <- html_text(names[name])
        crdata[[paste0("namesdate", name)]] = dmy(str_sub(tempname, 1, 10))
        tempname <- str_sub(tempname, 11)
        tempextract <- extractnames(tempname)
        crdata[[paste0("namesenglish", name)]] = tempextract[[1]]
        crdata[[paste0("nameschinese", name)]] = tempextract[[2]]
    }
    
    return(crdata)
}

#if (file.exists("scrapelist.Rdata")) {
#    load("scrapelist.Rdata")
#} else {
#    scrapelist <- data.table(crno = "0", companytype = "blah")
#    setkey(scrapelist, crno)
#}

maxcr = 2120960
mincr = 1 # scrapelist[,max(as.numeric(crno))]

scrapelist <- mclapply(mincr:maxcr, scrape)


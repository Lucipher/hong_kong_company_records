library(rvest)
library(lubridate)
library(stringr)

maxcr = 2120960
mincr = 1686538

scrape <- function(crno) {
    crnostr = sprintf("%07d", crno)
    baseurl = "https://www.mobile-cr.gov.hk/mob/cps_criteria.do?queryCRNO="
    url = paste0(baseurl, crnostr)

    print(c("trying local", crnostr))
    html <- html(url, encoding = "utf-8")

    if (!is.null(html_node(html, "body"))) {
        if (length(grep('沒有紀錄與輸入的查詢資料相符', html_text(html_node(html, "body"))) > 0)) {
            print('NO MATCHING RECORD FOUND FOR THE SEARCH INFORMATION INPUT!')
            return()
        }
    }

    tds <- html_text(html_nodes(html, "td:nth-child(2)"))
    deleteslashes <- function(x) {str_replace_all(x, "[\n\t\r]", "")}
    crdata <- list(crno = tds[1], companytype = deleteslashes(tds[2]), incorporationdate = dmy(tds[3]), status = deleteslashes(tds[4]), windingupmode = deleteslashes(tds[5]), dissolutiondate = dmy(tds[6]), registeravailable = deleteslashes(tds[7]))

    companyname <- str_replace(deleteslashes(html_text(html_node(html, "td tr:nth-child(2) td"))), "公司名稱：", "")
    crdata[["currentnameenglish"]] <- str_extract(companyname, "[A-Z'\- ]+")
    crdata[["currentnamechinese"]] <- str_replace(companyname, crdata[["currentnameenglish"]], "")

    names <- html_nodes(html, ".data")
    namesenglish <- c()
    nameschinese <- c()
    namesdates <- c()
    for (name in 1:length(names)) {
        tempname <- html_text(names[name])
        namesdates[name] <- str_sub(tempname, 1, 10)
        tempname <- str_sub(tempname, 11)
        namesenglish[name] <- str_extract(tempname, "[A-Z'\- ]+")
        nameschinese[name] <- str_replace(tempname, namesenglish[name], "")
    }

    crdata["namesdates"] <- namesdates
    crdata["namesenglish"] <- namesenglish
    crdata["nameschinese"] <- nameschinese

    return(crdata)
}

scrapelist <- list()
for(crno in (1:10)) {
    scrapelist[[crno]] <- scrape(crno)
}

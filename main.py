import logging
import smtplib
import urllib2
from datetime import datetime
from time import strftime

from lxml import etree


def get_last_update(get_url):
    try:
        logit('Getting info from url...')
        response = urllib2.urlopen(get_url)
        htmlparser = etree.HTMLParser()
        tree = etree.parse(response, htmlparser)
        selection = tree.xpath('//*[@id="cmbOdabirDokumenata236"]/ul[1]/li')
        result = {}

        for a in selection:
            date = a[0].text
            tmp_url = a[1].getchildren()[0].get('href')
            tmp = date.split('.')
            datetime_obj = datetime(int(tmp[2]), int(tmp[1]), int(tmp[0]))
            result[datetime_obj] = tmp_url

        tmp_date = max(result.keys())
        return tmp_date, result[tmp_date]

    except Exception, e:
        logit('Failed getting info from url... - ' % e.message)
        return '', ''


def send_mail(gmail_user, gmail_pwd, recipient, text):
    g_from = gmail_user
    g_to = recipient if type(recipient) is list else [recipient]
    g_subject = 'Delegiranje update'

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (g_from, ", ".join(g_to), g_subject, text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(g_from, g_to, message)
        server.close()
        return 0, ''
    except Exception, e:
        return 1, e.message


def logit(message):
    logging.debug("%s -- %s" % (strftime("%d.%m.%Y %H:%M:%S"), message))


logging.basicConfig(filename='log', level=logging.DEBUG)
url = 'http://hns-cff.hr/hns/suci/'
pwd_last_date = 'lastupdate'
last_date, last_date_url = get_last_update(url)

# Fix URL (remove whitespace)
fixed_url = ''
for char in last_date_url:
    if char == ' ':
        char = '%20'
    fixed_url += char

file0 = open(pwd_last_date)
stored_date = file0.read().strip()
file0.close()

logit("Stored date: %s ; Got date: %s" % (stored_date, last_date))
if stored_date != str(last_date):
    logit('Alerting...')
    gm_user = 'xxxxxxxxx@gmail.com'
    gm_pwd = 'xxxxxxxxx'
    send_to = 'xxxxxxxxx@gmail.com'
    msg = 'Zadnji update: %s\nhttp://hns-cff.hr%s' % (last_date.strftime("%d.%m.%Y"), fixed_url)
    logit('Sending e-mail... Message: %s' % msg)
    res, msg = send_mail(gm_user, gm_pwd, send_to, msg)
    if not res:
        logit('Mail successfully sent')
        file1 = open(pwd_last_date, 'w')
        print >> file1, last_date
        file1.close()
    else:
        logit('E-mail sending failed - %s' % msg)
else:
    logit('Not alerting...')

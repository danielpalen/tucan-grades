from email.header import Header
from email.mime.text import MIMEText
import json
import os
from robobrowser import RoboBrowser
import smtplib


def open_page(url, browser):
    """This function opens a relative url on the tucan homepage and follows
    optional redirects."""
    browser.open('https://www.tucan.tu-darmstadt.de' + url)
    redirect = browser.find( 'meta', { 'http-equiv' : 'refresh' } )
    if redirect:
        redirect_path = redirect['content'].split('URL=')[1]
        print('redirect to ', redirect_path)
        open_page(redirect_path, browser)


def login(usr, pwd, browser):
    """This function logs into the tucan page for the specified user."""
    login_form = browser.get_form(id='cn_loginForm')
    login_form['usrname'].value = usr
    login_form['pass'].value = pwd
    browser.submit_form(login_form)
    open_page( browser.response.headers['REFRESH'].split('URL=')[1], browser )


def get_grades(user, password):
    """This function navigates through tucan and gets and returns all the grades."""

    # Navigate to the grades page.
    browser = RoboBrowser(history=True)
    open_page('', browser)
    login(user, password, browser)
    tests_link = browser.find('a', { 'class' : 'link000280'} )
    browser.follow_link(tests_link)
    scores_link = browser.find('a', { 'class' : 'link000316' } )
    browser.follow_link(scores_link)

    # Extract the grades.
    grades = []
    for row in browser.select('tr'):
        td = row.select('td')
        # Only subjects to have 7 td items. The rest are seperators.
        if len(td) == 7:
            subject = {
                'id'      : td[0].text,
                'subject' : td[1].text.replace('\t','').replace('\r','').split('\n')[1].strip(),
                'cp'      : td[3].text.strip(),
                'grade'   : td[5].text.strip()
            }
            grades.append(subject)
    return grades


def send_mail(user, password, email, tucan_email, grades):
    """Sends an email containing a list of grades."""
    text = ''

    for grade in grades:
        text += '- {}:\t {}\n'.format( grade['subject'], grade['grade'] )

    msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['From']    = tucan_email
    msg['To']      = email
    msg['Subject'] = Header('Neue Ergebnisse', 'utf-8')
    smtp = smtplib.SMTP_SSL('smtp.tu-darmstadt.de', 465)
    smtp.login(user, password)
    smtp.sendmail(tucan_email, email, msg.as_string())
    smtp.quit()


def get_old_grade_ids(user):
    """Gets the old grade ids of the grades that exisited already."""
    if os.path.isfile('grade-ids/{}.json'.format(user)):
        with open('grade-ids/{}.json'.format(user)) as f:
            return json.load(f)
    else:
        print('File does not exist:', user)
        return []


def save_grade_ids(user, grades):
    """Extracts and saves all the grade ids from a list of grades."""
    ids = [ g['id'] for g in grades ]

    try:
        os.mkdir('grade-ids')
    except Exception:
        pass

    with open('grade-ids/{}.json'.format(user), 'w') as f:
        json.dump(ids, f)


def which_grades_are_new(user, grades):
    """Determines, which grades are new and returns them in a list."""
    new_grades = [ g for g in grades if not g['id'] in get_old_grade_ids(user) ]
    if new_grades:
        print('need to persist')
        save_grade_ids(user, grades)
    return list(new_grades)


if __name__ == '__main__':
    with open('config.json') as f:
        for account in json.load(f):

            user        = account['user']
            password    = account['password']
            tucan_email = account['tucan_email']
            email       = account['email']

            grades     = get_grades(user, password)
            new_grades = which_grades_are_new(user, grades)
            if new_grades:
                send_mail(user, password, email, tucan_email, new_grades)
                print('new grades email sent.')
            else:
                print('no new grades.')

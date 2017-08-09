from email.header import Header
from email.mime.text import MIMEText
import json
import os
from robobrowser import RoboBrowser
import smtplib


def open_page(url):
    """This function opens a relative url on the tucan homepage and follows
    optional redirects."""
    browser.open('https://www.tucan.tu-darmstadt.de' + url)
    redirect = browser.find( 'meta', { 'http-equiv' : 'refresh' } )
    if redirect:
        redirect_path = redirect['content'].split('URL=')[1]
        print('redirect to ', redirect_path)
        open_page(redirect_path)


def login(usr, pwd):
    """This function logs into the tucan page for the specified user."""
    login_form = browser.get_form(id='cn_loginForm')
    login_form['usrname'].value = usr
    login_form['pass'].value = pwd
    browser.submit_form(login_form)
    open_page( browser.response.headers['REFRESH'].split('URL=')[1] )


def get_grades():
    """This function navigates through tucan and gets and returns all the grades."""

    # Navigate to the grades page.
    open_page('')
    login(user, password)
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


def send_mail(grades):
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


def get_old_grade_ids():
    """Gets the old grade ids of the grades that exisited already."""
    if os.path.isfile('grade-ids.json'):
        with open('grade-ids.json') as f:
            return json.load(f)
    else:
        return []


def save_grade_ids(grades):
    """Extracts and saves all the grade ids from a list of grades."""
    ids = [ g['id'] for g in grades ]
    with open('grade-ids.json', 'w') as f:
        json.dump(ids, f)


def which_grades_are_new(grades):
    """Determines, which grades are new and returns them in a list."""
    old_grade_ids = get_old_grade_ids()
    new_grades = [ g for g in grades if not g['id'] in old_grade_ids ]

    if new_grades:
        print('need to persist')
        save_grade_ids(grades)

    return list(new_grades)


if __name__ == '__main__':
    browser = RoboBrowser(history=True)

    with open('config.json') as f:
        config = json.load(f)
        user        = config['user']
        password    = config['password']
        tucan_email = config['tucan_email']
        email       = config['email']

        grades = get_grades()
        new_grades = which_grades_are_new(grades)
        if new_grades:
            send_mail(new_grades)
            print('new grades email sent.')
        else:
            print('no new grades.')

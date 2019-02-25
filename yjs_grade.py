#!/usr/bin/env python3
import logging
import time

import requests
from bs4 import BeautifulSoup

import config
from mail import send_email

s = requests.session()


def cas_login():
    logging.info('Logging in')
    url = 'https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp'
    r = s.get(url, timeout=config.req_timeout)
    soup = BeautifulSoup(r.content, 'html5lib')
    token = soup.find('input', {'name': '_token'})['value']
    r = s.post(url, data={'_token': token, 'login': config.student_no, 'password': config.cas_password},
               timeout=config.req_timeout)
    if r.url == 'http://yjs.ustc.edu.cn/main.asp':
        logging.info('Login success')
        return True
    else:
        logging.error('Login failed')
        return False


def get_grade():
    r = s.get('http://yjs.ustc.edu.cn/score/m_score.asp', timeout=config.req_timeout)
    soup = BeautifulSoup(r.content, 'html5lib')
    grades = {}
    for row in soup.find_all('table')[-1].find_all('tr')[1:]:
        cols = row.find_all('td')
        name = cols[3].text
        grade = cols[4].text
        grades[name] = grade
    return grades


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')
    last_grades = {}
    first_run = True
    cas_login()
    while True:
        try:
            try:
                logging.info('Fetching grades')
                grades = get_grade()
                logging.info('Count = %s', len(grades))
            except Exception as e:
                logging.warning('Error occurred, trying to login again')
                cas_login()
            else:
                test_mail = False
                if first_run:
                    ans = input('Send test email? (y/n)')
                    if ans.lower() in ['', 'y', 'yes']:
                        test_mail = True
                if (not first_run and grades != last_grades) or test_mail:
                    text = ', '.join(name + ' ' + grade for name, grade in grades.items() if name not in last_grades)
                    logging.info('Sending email: %s', text)
                    if config.enable_mail:
                        send_email(text, text)
                        logging.info('Mail sent')
                last_grades = grades
                first_run = False
            finally:
                time.sleep(config.interval)
        except Exception as e:
            logging.exception(e)

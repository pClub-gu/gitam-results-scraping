import argparse
import os
import sys

import BeautifulSoup
import rethinkdb as r
import requests

RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
resultsdb = 'resultsdb'


def dbSetup():
    connection = r.connect(host=RDB_HOST, port=RDB_PORT)
    try:
        r.db_create(resultsdb).run(connection)
        
        r.db(resultsdb).table_create('results').run(connection)
        r.db(resultsdb).table_create('gpa').run(connection)
        r.db(resultsdb).table_create('students', primary_key='regno').run(connection)

        r.db(resultsdb).table('gpa').index_create(
            'semester_',
            [
                r.row["regno"],
                r.row["semester"]
            ]
            ).run(connection)
        r.db(resultsdb).table('results').index_create(
            'subject',
            [
                r.row["regno"],
                r.row["code"],
                r.row["subject_name"]
            ]
            ).run(connection)
        
        print ('Database setup completed. Now run the app without --setup: '
               '`python downloaddb.py`')
    except r.RqlRuntimeError, e:
        print e
        #print ('App database already exists. Run the app without --setup: '
               #'`python downloaddb.py`')
    finally:
        connection.close()


def connectDb():
    try:
        rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=resultsdb)
        return rdb_conn
    except r.RqlDriverError:
        raise Exception("No database connection could be established.")


def return_soup(id_sem_tuple):
    id = id_sem_tuple[0]
    sem = id_sem_tuple[1]
    url = "http://doeresults.gitam.edu/onlineresults"
    url += "/pages/NewReportviewer1.aspx?"
    url += "&sem={sem}&reg={id}".format(sem=str(sem), id=str(id))
    r = requests.get(url)
    data = r.text

    soup = BeautifulSoup.BeautifulSoup(data)
    spans = soup.findAll('span')
    if not spans:
        return None
    elements = [a.b.font.contents[0].encode('utf-8') for a in spans[:-3]]
    elements = [x.replace('&nbsp;', ' ') for x in elements]
    elements = [x.replace('&#x200E;', ' ') for x in elements]
    elements = [x.replace('&amp;', '&') for x in elements]
    if id_sem_tuple[1] == 2:
        elements = [x.decode('utf-8').replace(u'\u2013', '-').encode('utf-8') for x in elements]
    elements = [x.strip() for x in elements]
    elements = filter(lambda x: x != ':', elements)
    elements = filter(lambda x: x != '/', elements)
    return elements


def result_scraper(id_sem_tuple):
    elements = return_soup(id_sem_tuple)
    if not elements:
        return None
    raw_grades = elements[-4:]
    raw_subjects = elements[22:-4]
    raw_headers = elements[:18]
    subjects = []
    for num in xrange(0, len(raw_subjects), 4):
        subjects.append({
            'regno': raw_headers[15],
            'code': raw_subjects[num],
            'subject': raw_subjects[num+1],
            'credits': raw_subjects[num+2],
            'grade': raw_subjects[num+3]
            })
    grades = {
        'regno': raw_headers[15],
        'semester': raw_headers[4],
        'GPA': raw_grades[1],
        'CGPA': raw_grades[3]
    }

    result = {}
    result['grades'] = grades
    result['subjects'] = subjects
    return result


def student_scraper(id_sem_tuple):
    elements = return_soup(id_sem_tuple)
    if not elements:
        return None
    raw_headers = elements[:18]
    headers = {
        'name': raw_headers[13],
        'regno': raw_headers[15],
        'course': raw_headers[2],
        'semester': raw_headers[4],
        'branch': raw_headers[17]
    }
    return headers


def scrape_students(connection, replace):
    gen = foo_generator()
    id_sem = next(gen)
    while id_sem:
        student = student_scraper(id_sem)
        if student is None:
            print id_sem
        else:
            if replace:
                inserted = r.db(resultsdb).table('students').insert(student, conflict="replace")
            else:
                inserted = r.db(resultsdb).table('students').insert(student, conflict="error")
            inserted.run(connection)
            print {id: inserted['generated_keys'][0]}
            print "stored headers for: {id} ".format(id=str(id_sem[0]))
        id_sem = next(gen)

def scrape_results(connection, replace):
    gen = foo_generator()
    id_sem = next(gen)
    while id_sem:
        for x in range(1, id_sem[1] + 1):
            result = result_scraper((id_sem[0], x))
            if result is None:
                print "[x] Error with {x}".format(x=str(id_sem[0]))
            else:
                print "[y] Storing for id: "
                store_results(result, connection, replace)
        else:
            print "stored result for: {id} ".format(id=str(id_sem[0]))
        id_sem = next(gen)
    else:
        print "All ids done!"


def store_results(result, connection, replace=False):
    ins_ = 0
    for subj in result['subjects']:
        if replace:
            inserted = r.db(resultsdb).table('results').insert(subj, conflict="replace")
        else:
            inserted = r.db(resultsdb).table('results').insert(subj, conflict="error")
        ins = inserted.run(connection)
        ins_ += ins['inserted']
    print 'inserted: %d' % ins_
    if replace:
        inserted = r.db(resultsdb).table('gpa').insert(result['grades'], conflict="replace")
    else:
        inserted = r.db(resultsdb).table('gpa').insert(result['grades'], conflict="error")
    ins = inserted.run(connection)

    print ins['inserted']


def foo_generator():
    cse = '12103'
    years = {
        '11': 5,
        '12': 6,
        '13': 9
    }
    rnos = 67
    # reference : 1210-31-26-39
    for year in years:
        for section in range(1, years[year]+1):
            for rno in range(1, rnos+1):
                rn = str(rno)
                if len(rn) == 1:
                    rn = '0' + rn
                id = cse + str(year) + str(section) + rn
                sem = 0
                if year == '11':
                    sem = 6
                elif year == '12':
                    sem = 4
                elif year == '13':
                    sem = 2
                yield (id, sem)


def main(options, replace):
    connection = connectDb()
    if options['students']:
        scrape_students(connection, replace)
    if options['results']:
        scrape_results(connection, replace)
    print 'All done!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--setup', dest='run_setup', action='store_true')
    parser.add_argument('--replace', dest='replace', action='store_true')
    parser.add_argument('--students', dest='students', action='store_true')
    parser.add_argument('--results', dest='results', action='store_true')
    args = parser.parse_args()
    if args.run_setup:
        dbSetup()
    elif not (args.results or args.students):
        print 'Either --students or --results has to be specified'
        sys.exit(0)
    else:
        options = {}
        options['students'] = args.students
        options['results'] = args.results
        main(options, args.replace)

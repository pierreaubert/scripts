#                                                                    -* python -*-
# this script takes all authors from my calibre library and search from new books 
# in a sff update
# first pass is with author exact match then
# second pass try to guess for example matching 
#    'a.g. x' with 'a. g. x' or 'arthur anton x'.
# --------------------------------------------------------------------------------

import glob
import os
import re
import itertools
import argparse

opts_parser = argparse.ArgumentParser(description='Scan your calibre collection \
and try to find matches in SFF large collection.')
opts_parser.add_argument(
    "-d", "--debug", help='add (a lot) of traces', dest='debug',
    action="store", default=False)
opts_parser.add_argument(
    "-v", "--verbose", help='add (a lot) of details',
    action="store_true", default=False)
opts_parser.add_argument(
    "-D", "--display", help='linear or grouped display', dest='display',
    choices=['linear', 'grouped'], action="store", default='grouped')
opts_parser.add_argument(
    "--calibre", help='calibre directory path', dest='calibre',  action="store")
opts_parser.add_argument(
    "--sff", help='SFF directory path', dest='sff', action="store")
opts_parser.add_argument(
    "-A", "--author", help='1 specific author to look at', action="store_true")
opts = None

dir_calibre = '{home}/Calibre'.format(home=os.environ['HOME'])
dir_sffupdate = '{home}/sff'.format(home=os.environ['HOME'])

# a re for looking for initials
pattern_initiales = re.compile(r"([A-Z](\.|_| ))+")

# a re to split author names
pattern_authors_splitter = re.compile(r";|&")

# colors
C_NORMAL='\033[30m'
C_RED='\033[31m'
C_GREEN='\033[32m'
C_BLUE='\033[34m'

def scan_dir(path):
    """
    # build a list of all dirs in *path*
    # basename is usually a author name
    """
    r = []
    # could use listdir
    dirs = glob.glob(path+'/*')
    for d in dirs:
        if os.path.isdir(d):
            r.append(os.path.basename(d).strip())
    return r


def sff_author_to_title(book):
    """
    # takes a sff *book*'s name and lookup for title
    # usually        
    #       author is the last field minus # ... .epub
    # example:
    #       author - series - title # version.(epub|mobi|...)
    """
    pos = book.rfind('#')
    if pos == -1:
        pos = book.rfind('.')
    if pos == -1:
        pos = len(book)
    bs = book[0:pos].split('-')
    title = bs[len(bs)-1]
    # print('book: {0} title: {1}'.format(book, title))
    return title.strip().lower()
    

def calibre_author_to_title(book):
    """
    # takes a calibre *book*'s name and lookup for title
    # normally it is only a title followed by type
    """
    pos = book.rfind('.')
    if pos == -1:
        pos = len(book)
    return book[0:pos].split('-')


def check(author, book_sff):
    """ return true if it looks like *book* from *author* exist in calibre """
    title_sff = sff_author_to_title(book_sff)
    books_calibre = []
    for f in glob.glob(dir_calibre+'/*'+author['calibre']+'*/*/*.*'):
        if os.path.isfile(f):
            calibre_titles = calibre_author_to_title(os.path.basename(f))
            for calibre_title in calibre_titles:
                books_calibre.append(calibre_title.strip().lower())
#    print(title_sff)
#    print(set(books_calibre))
    return title_sff not in set(books_calibre)


def scan(author_link):
    """
    display *author* and corresponding names
    """
    author = author_link['sff'].strip()
    author_dir = dir_sffupdate+'/'+author
    if not os.path.isdir(author_dir):
        print(u'author is incorrect: directory {0} doesn\'t exist!'.format(author_dir))
        return []
    ll = []
    for f in glob.glob(dir_sffupdate+'/'+author+'/*'):
        # print('tracking files: {0}'.format(f))
        if os.path.isfile(f):
            b = os.path.basename(f)
            status = check(author_link, b)
            ll.append([status, b])
    return ll


def display_book(color, title):
    return '''- {color}NEW{normal} - {title}'''.format(
        color=color,
        normal=C_NORMAL,
        title=title)

def display_linear(status_title):
    for l in status_title:
        status = l[0]
        title = l[1]
        if status:
            print('    {0}'.format(display_book(C_GREEN, title)))
        else:
            print('    {0}'.format(display_book(C_BLUE, title)))

def iter_group_on_title(dtitle):
    r = None
    if opts.debug: 
        print('(debug) {0}'.format(str(dtitle)))
    dot   = dtitle['title'].split('.')
    sharp = dot[0].split('#')
    if len(sharp) == 2:
        r = sharp[0]
    else:
        r = dot[0]
    return r.strip()


def group_by_title(ltitles):
    titles = []
    for t, isuffix in itertools.groupby(ltitles, iter_group_on_title):
        raw = list(isuffix)
        extra = None
        sharp  = raw[0]['title'].split('#')
        if len(sharp) > 1:
            extra = '.'.join(sharp[1].split('.')[0:-1]).strip()
        suffix = [r['title'].split('.')[-1] for r in raw]
        titles.append({'title': t,
                       'suffix': suffix,
                       'number': raw[0]['number'],
                       'status': raw[0]['status'],
                       'extra': extra,
        })
    # print(titles)
    return titles


def remove_last_number(s):
    # remove last serie number
    t = s.strip()
    f = [i.start() for i in re.finditer(' [0-9]+([.][0-9]+)?', t)]
    if len(f) == 0:
        return t
    else:
        return t[0:f[-1]].strip()


def grab_last_number(s):
    # return serie number or None
    t = s.strip()
    f = [i.start() for i in re.finditer(' [0-9]+([.][0-9]+)?', t)]
    if len(f) == 0:
        return None
    r = t[f[-1]:].strip()
    try:
      float(r)
      return r
    except ValueError:
        return None
        

def iter_group_on_collection(status_title):
    # return an iterator breaking on collection
    title = status_title[1]
    splitted = title.split('-')
    l = len(splitted)
    if l == 2:
        return '__none__'
    elif l > 2:
        if opts.debug: 
            print('(debug) |{0}| and |{1}|'.format(splitted[1], remove_last_number(splitted[1])))
        return remove_last_number(splitted[1])
    else:
        print('(error) splitted len\'s={0} for {1}, don\'t know what to do!'.format(l, title))


def group_by_collection(status_title):
    groups = []
    for collection, ititles in itertools.groupby(status_title, iter_group_on_collection):
        raw = list(ititles)
        titles = []
        for r in raw:
            title  = None
            number = None
            status = r[0]
            work   = r[1].split('-')
            if collection == '__none__':
                title = work[1].strip()
            else:
                number = grab_last_number(work[1])
                title = work[2].strip()
            titles.append({
                'title': title,
                'number': number,
                'status': status,
            })
        if opts.debug: 
            print('(debug) collection {0} titles {1}'.format(collection, str(titles)))
        groups.append({
            'collection': collection,
            'titles': group_by_title(titles),
        })
    # print(groups)
    return groups


def display_grouped(status_title):
    # try to make a more sexy display
    groups = group_by_collection(status_title)
    cnt_books = 0
    cnt_series = 0
    for group in groups:
        if group['collection'] == '__none__':
            cnt_books += 1
        else:
            cnt_series += 1

    if cnt_books > 0:
        print('  Books')
    for group in groups:
        collection = group['collection']
        if collection == '__none__':
            raw_title = group['titles'][0]
            title = None
            if len(raw_title['suffix']) == 1:
                title = '{0}.{1}'.format(raw_title['title'], raw_title['suffix'][0])
            else:
                title = '{0}.({1})'.format(raw_title['title'], '|'.join(raw_title['suffix']))
            if raw_title['status']:
                print('          {0}'.format(display_book(C_GREEN, title)))
            else:
                print('          {0}'.format(display_book(C_BLUE, title)))


    if cnt_series > 0:                
        print('  Series')
    for group in groups:
        collection = group['collection']
        if collection != '__none__':
            cnt_new = 0
            cnt_upd = 0
            for raw_title in group['titles']:
                if raw_title['status']:
                    cnt_new += 1
                else:
                    cnt_upd += 1
            print(u'''    - {0} ({1} new + {2} update)'''.format(collection,cnt_new, cnt_upd))
            for raw_title in group['titles']:
                title = None
                if len(raw_title['suffix']) == 1:
                    title = '{0}.{1}'.format(raw_title['title'], raw_title['suffix'][0])
                else:
                    title = '{0}.({1})'.format(raw_title['title'], '|'.join(raw_title['suffix']))
                if raw_title['status']:
                    print(u'''        - {green}NEW{normal} - {number} - {title}'''.format(green=C_GREEN,
                                                                                          normal=C_NORMAL,
                                                                                          number=raw_title['number'],
                                                                                          title=title))
                else:
                    print(u'''        - {blue}UPD{normal} - {number} - {title}'''.format(blue=C_BLUE,
                                                                                         normal=C_NORMAL,
                                                                                         number=raw_title['number'],
                                                                                         title=title))
            

def display(author_link, option):
    author = author_link['sff'].strip()
    print(u'{red}{author}{normal}'.format(red=C_RED, normal=C_NORMAL, author=author))
    status_title = scan(author_link)
    if option == 'linear':
        display_linear(status_title)
    else:
        display_grouped(status_title)


def match_authors(calibre_author, sff_author):
    """
    return true if authors in both formatting match
    """
    calibre = calibre_author.lower()
    sff = sff_author.lower()
    # 0/ easy case
    if calibre == sff:
        return True
    # 1/ split on '&' or '-' in case of multiple authors
    # 2/ if we have a ',' reverse name and forname
    # 3/ expect name to match, a few guesses for fornames
    sff_split_on_space = sff.split(' ')
    sff_name = sff_split_on_space[-1]
    sff_fornames = sff_split_on_space[1]
    calibre_split_on_space = calibre.split(' ')
    calibre_name = calibre_split_on_space[-1]
    calibre_fornames = calibre_split_on_space[1]
    #   a/ remove space                      A.G. Riddle -> A. G. Riddle
    if calibre_name == sff_name and calibre_fornames.replace(' ', '') == sff_name.replace(' ', ''):
            return True
    #   b/ try to remove last forname        Jules Amedee Barbey d'Aurevilly ->  Jules Barbey d'Aurevilly
    #   c/                                   Jules Amedee Barbey d'Aurevilly ->  J.A. Barbey d'Aurevilly
    # 4/ do we have a match if we swap name and forname? 
    # failed
    return False


def lookslikeinitial(lemme):
    # return true if it looks like some initials
    # L.P.
    # L. P.
    # L. P_
    return pattern_initiales.search(lemme) != None


def to_sff(calibre_author):
    """
    # transform a calibre author into a sff formated author
    # first check for .
    #       A.G. Riddle -> A. G. Riddle

    # we split on space first
    # and scan all blocks except last
    # notice that the match is not perfect at all
    """
    pos = calibre_author.find('.')
    if pos == -1:
        return calibre_author
    # BUG BUG


def normalize_author(calibre_author):
    name = calibre_author.strip()
    # take care of double spaces
    name = ' '.join(name.split())
    parts = name.split(' ')
    if opts.debug: 
        print(u'(debug) "{0}" {1} parts'.format(name, len(parts)))
    if len(parts) == 1:
        return [name.title()]
    elif len(parts) == 2:
        # generate 2 solutions
        # P. Nom
        # Prenom Nom
        prenom = parts[0].title()
        nom = parts[1].title()
        if lookslikeinitial(prenom):
            initiales = prenom.split('.')
            prenom_sff = '. '.join(initiales)
            return ['{0}{1}'.format(prenom_sff, nom),
                    '{0}. {1}'.format(prenom[0], nom),
            ]
        else:
            return ['{0} {1}'.format(prenom, nom),
                    '{0}. {1}'.format(prenom[0], nom),
            ]
    else:
        # generate N solutions
        # Prenom Second Third Nom
        # Prenom S. T. Nom
        # P. S. T. Nom
        prenom = parts[0].title()
        second = parts[1].title()
        second_sff = second
        if lookslikeinitial(second):
            initiales = second.split('.')
            second_sff = '. '.join(initiales)
        nom = parts[-1].title()
        if opts.debug: 
            print(u'(debug) prenom={0} nom={1}'.format(prenom, nom))
        if len(parts) == 3:
            if second == second_sff:
                return ['{0} {1}'.format(prenom, nom),
                        '{0}. {1}'.format(prenom[0], nom),
                        '{0} {1}. {2}'.format(prenom, second[0], nom),
                        '{0}. {1}. {2}'.format(prenom[0], second[0], nom),
                        '{0} {1} {2}'.format(prenom, second, nom),
                ]
            elif second == 'Von' or second == 'Van':
                return ['{0} {1}'.format(prenom, nom),
                        '{0}. {1}'.format(prenom[0], nom),
                        '{0} {1}. {2}'.format(prenom, second[0], nom),
                        '{0}. {1}. {2}'.format(prenom[0], second[0], nom),
                        '{0} {1} {2}'.format(prenom, second, nom),
                        '{0} {1} {2}'.format(prenom, second.lower(), nom),
                ]
            else:
                return ['{0} {1}'.format(prenom, nom),
                        '{0}. {1}'.format(prenom[0], nom),
                        '{0} {1}. {2}'.format(prenom, second[0], nom),
                        '{0}. {1}{2}'.format(prenom[0], second_sff, nom),
                        '{0} {1}{2}'.format(prenom, second_sff, nom),
                ]
        else:
            if len(second) == 1:
                second = '{0}.'.format(second)
            troisieme = parts[2].title()
            if troisieme == 'Von' or troisieme == 'Van':
                return ['{0} {1}'.format(prenom, nom),
                        '{0}. {1}'.format(prenom[0], nom),
                        '{0} {1} {2}'.format(prenom, second, nom),
                        '{0} {1}. {2} {3}'.format(prenom, second[0], troisieme, nom),
                        '{0} {1}. {2} {3}'.format(prenom, second[0], troisieme.lower(), nom),
                        '{0} {1}. {2}. {3}'.format(prenom, second[0], troisieme[0], nom),
                        '{0}. {1}. {2}. {3}'.format(prenom[0], second[0], troisieme[0], nom),
                        '{0}. {1}. {2} {3}'.format(prenom[0], second[0], troisieme, nom),
                        '{0}. {1}. {2} {3}'.format(prenom[0], second[0], troisieme.lower(), nom),
                        '{0} {1} {2} {3}'.format(prenom, second, troisieme, nom),
                        '{0} {1} {2} {3}'.format(prenom, second, troisieme.lower(), nom),
                ]
            else:
                return ['{0} {1}'.format(prenom, nom),
                        '{0}. {1}'.format(prenom[0], nom),
                        '{0} {1} {2}'.format(prenom, second, nom),
                        '{0} {1}. {2} {3}'.format(prenom, second[0], troisieme, nom),
                        '{0} {1}. {2}. {3}'.format(prenom, second[0], troisieme[0], nom),
                        '{0}. {1}. {2}. {3}'.format(prenom[0], second[0], troisieme[0], nom),
                        '{0}. {1}. {2} {3}'.format(prenom[0], second[0], troisieme, nom),
                        '{0} {1} {2} {3}'.format(prenom, second, troisieme, nom),
                ]                
            

    
def normalize_authors(calibre_authors):
    """
    take a author in calibre format and generate a few guess on how it should be in sff
    """
    results = None
    # split on , and count answers
    authors = calibre_authors.split(',')
    if len(authors) > 2:
        # like 3 or more authors
        guesses = [normalize_author(a) for a in authors]
        results = [g for gs in guesses for g in gs]
    elif len(authors) == 2:
        # 2 authors is ambiguous
        cnt_1 = len(authors[0].split(' '))
        cnt_2 = len(authors[1].split(' '))
        if cnt_1 > 1 and cnt_2 > 1:
            # most likely 2 authors
            results = normalize_author(authors[0])+normalize_author(authors[1])
        else:
            results = normalize_author('{1} {0}'.format(authors[0].strip(),
                                                        authors[1].strip()))
    else:
        # do we have a clear separator between authors? like ; or & ?
        authors = pattern_authors_splitter.split(calibre_authors)
        guesses = [normalize_author(a) for a in authors]
        results = [g for gs in guesses for g in gs]
    if opts.debug: 
        print(u'(debug) "{0} [{1}]"'.format(calibre_authors, ', '.join(results)))
    return results


def lookup_match_authors(d_calibre, d_sff):
    # per author, compute intersection length between set of possible matches
    exact_authors = []
    notfound_authors = []
    for a in d_calibre:
        sa = normalize_authors(a)
        inter = set(sa).intersection(d_sff)
        if len(inter) > 0:
            sff = inter.intersection(d_sff)
            exact_authors.append({'calibre': a, 'sff': sff.pop()})
            if opts.debug: 
                print('(debug) {0} match {1}'.format(a, sa[0]))
        else:
            notfound_authors.append(a)
            if opts.debug: 
                print('(debug) {0} -> {1} doesnt match'.format(a, ' '.join(sa)))
    return exact_authors, notfound_authors


if __name__ == '__main__':

    opts = opts_parser.parse_args()

    # list of all authors in Calibre
    if opts.calibre:
        dir_calibre = opts.calibre
    d_calibre = scan_dir(dir_calibre)
    
    # list of all authors in SFF
    if opts.sff:
        dir_sffupdate = opts.sff
    d_sff = set(scan_dir(dir_sffupdate))

    exact_authors, notfound_authors = lookup_match_authors(d_calibre, d_sff)

    print('{0} authors in Calibre, {1} authors in new sff update, found {2} authors in both'\
          .format(len(d_calibre), len(d_sff), len(exact_authors)))
    if opts.debug: 
        print(notfound_authors)

    for author in exact_authors:
        display(author, opts.display)

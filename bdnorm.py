#!/usr/bin/python
# -*- coding: utf-8 -*-
# normalise names in comics directory
# convention is as follow
#    series/Series_01_Title.suf
# Author: P. Aubert pierreaubert@yahoo.fr
# Apache 2 License
# ----------------------------------------------------------------------
import os
import sys
import re
import glob
import codecs
import unicodedata
import argparse

opts_parser = argparse.ArgumentParser(description='This script will normalize the name of your collection of comics. \
By default it will just show the proposed names. If you want to force the actual conversion user the force flag.')
opts_parser.add_argument("-f", "--force", help='Rename files', action="store_true")
opts_parser.add_argument("-d", "--debug", help='add (a lot) of traces', action="store_true")
opts_parser.add_argument("directory", help="Directory where the comics are")
opts = None

# separator, a . is allowed but only if followed by something else
regsep = r"""[.]?[-_\s]+[.]?"""

# ----------------------------------------------------------------------
# dict of stopwords
# ----------------------------------------------------------------------
stopwords_fr = ['de', 'le', 'la', 'les', 'a', 'du', 'ou', 'l', 'd',
                'et', 'des', 'au', 'aux']
stopwords_en = ['the', 'a', 'his', 'her', 'this', 'on']

stopwords = set(stopwords_fr + stopwords_en)


def to_ascii(text):
    """
    return text
    return text.replace(u'â','a')
    the official smart solution
    """
    #b = text.encode('utf-16', 'surrogatepass').decode('ascii', 'ignore')
    #return "".join( chr(x) for x in b)
    b = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return "".join( chr(x) for x in b)
 

def capitalize_first(text):
    """ capitalize text with exceptions """
    if text == text.upper():
        answer = text
    else:
        answer = text.title()

    return answer


def capitalize(text):
    """ capitalize text with exceptions """
    answer = ''
    if text.lower() in stopwords:
        answer = text.lower()
    elif text == text.upper():
        answer = text
    else:
        answer = text.title()
    return answer


def pretty(text):
    """
        pretty print title/serie
           remove trailing and leading spaces
           replace remaning spaces by .
           capitalize first word and all following words if not stopwords
    """

    answer = ''
    reg = re.compile(r'\W+', re.UNICODE)

    # transform to ascii first, the above regexp do not work as
    # i understand it should
    lexemes = reg.split(to_ascii(text))
    # lexemes = reg.split(text)

    if lexemes:
        answer = capitalize_first(lexemes[0])
        for i in range(1, len(lexemes)):
            # if opts.debug: print u'{0} {1}'.format(lexemes[i],
            #                                   capitalize(lexemes[i]))
            answer = answer + '.' + capitalize(lexemes[i])
    return answer


class ParserForNumber:
    """
    interface class for all parser
    """

    def __init__(self, bdname):
        self.parsed = ['', '', '']
        self.bdname = bdname
        self.regtome = r"""(?:[vVtT](?:ome(?:s)?)?[-_ ]?)?"""
        self.regnumber = r"""(?P<number>\d{1,2})"""

    def parse(self):
        return False, self.parsed


class ParseSpecial1(ParserForNumber):
    """
    lookup for this special synthax
           V3 #3 (of 5)
    """
    def parse(self):
        regspec = r"""
        V(?P<number>\d+)\s+[#]\d+\s+[(]of\s\d+[)]
        """
        reg = re.compile(regspec, re.VERBOSE)
        # search do not always work because of possible multiple matches
        split = reg.search(self.bdname)
        # positive case, we have 1 match only
        if split:
            if len(split.groups()) == 1:
                # easy case
                if opts.debug:
                    print(('opts.debug: {0}'.format(split.groups())))
                if opts.debug:
                    print(('opts.debug: from {0} to {1}'.format(split.start(), split.end())))
                # be careful -1 here because of a leading space
                self.parsed[0] = self.bdname[0:split.start()-1]
                self.parsed[1] = split.group('number')
                self.parsed[2] = self.bdname[split.end():]
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print('ko 2 groups or more in reg Vn #n (of N)')
                return False, self.parsed
        if opts.debug:
            print('opts.debug: ParseSpecial1: split do not match on Vn #n (of N)')
        return False, self.parsed


class ParseSpecial2(ParserForNumber):
    """
    lookup for this special synthax
            - 023#045 -
    this one is complicated because it also match a series with a trailing
    number followed by the tome number
    by checking first we simplify greatly the main regexp
    """
    def parse(self):
        regspec = r"""
        (?P<number>\d+)[#]\d+
        """
        reg = re.compile(regsep + regspec + regsep, re.VERBOSE)
        split = reg.search(self.bdname)
        # positive case, we have 1 match only
        if split:
            if len(split.groups()) == 1:
                # easy case
                if opts.debug:
                    print(('opts.debug: {0}'.format(split.groups())))
                if opts.debug:
                    print(('opts.debug: from {0} to {1}'.format(split.start(), split.end())))
                # be careful -1 here because of a leading space
                self.parsed[0] = self.bdname[0:split.start()]
                self.parsed[1] = split.group('number')
                self.parsed[2] = self.bdname[split.end():]
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print('ko 2 groups or more in reg - N#P -')
            return False, self.parsed

        if opts.debug:
            print('opts.debug: ParseSpecial2: split do not match on - N#P -')
        return False, self.parsed


class ParseSpecialOf(ParserForNumber):
    """
    lookup for this special synthax
          n of m
          1 of 3
          01 (of 04)
    """
    def parse(self):
        regspec = r"""(?P<first>\d+)\s[(]?of\s\d+[)]?"""
        reg = re.compile(regspec, re.IGNORECASE | re.VERBOSE)
        split = reg.search(self.bdname)
        if split:
            l1 = len(split.groups())
            if opts.debug:
                print(('opts.debug: ParseSpecialOf: len={0} groups={1}'.format(l1, split.groups())))
            if l1 == 1:
                # easy case
                if opts.debug:
                    print(('opts.debug: ParseSpecialOf: from {0} to {1}'.format(split.start(), split.end())))
                # be careful -1 here because of a leading space
                self.parsed[0] = self.bdname[:split.start()-1]+self.bdname[split.end():]
                self.parsed[1] = split.group('first')
                self.parsed[2] = ''
                if opts.debug:
                    print(('opts.debug: ParseSpecialOf: {0}'.format(self.parsed[0])))
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print(('ko ParseSpecialOf {0} groups or more in reg - N#P -'.format(l1)))
            return False, self.parsed

        if opts.debug:
            print('opts.debug: ParseSpecialOf: split do not match on - N of P -')
        return False, self.parsed


class ParseSpecialHS(ParserForNumber):
    """
    lookup for this special synthax
    """
    def parse(self):
        reghs = r"""(?:T?)(?P<hs>HS)(\s*(?P<hsn>\d{1,2}))?"""
        reg = re.compile(regsep + reghs + regsep, re.IGNORECASE | re.VERBOSE)
        split = reg.search(self.bdname)
        # positive case, we have 1 match only
        if split:
            if len(split.groups()) == 3:
                # easy case
                if opts.debug:
                    print(('opts.debug: {0}'.format(split.groups())))
                self.parsed[0] = self.bdname[0:split.start()]
                if split.group('hsn'):
                    if opts.debug:
                        print(('opts.debug: hsn {0}'.format(split.group('hsn'))))
                    self.parsed[1] = split.group('hs')+split.group('hsn')
                else:
                    self.parsed[1] = split.group('hs')
                self.parsed[2] = self.bdname[split.end():]
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print(('ko {0} groups or more in hs'.format(len(split.groups()))))
                return False, self.parsed

        if opts.debug:
            print('opts.debug: ParseSpecialHS split do not match on - HS n - ')
        return False, self.parsed


class ParseNormalCase(ParserForNumber):
    """
    lookup for the normal case
    """
    def parse(self):
        reg1 = re.compile(regsep + self.regtome + self.regnumber + regsep, re.VERBOSE)

        # search do not always work because of possible multiple matches
        split1 = reg1.search(self.bdname)

        # positive case, we have 1 match only
        if split1:
            # check if we have more than one number
            split11 = reg1.search(self.bdname[split1.end():])
            if split11:
                # aie: difficult to guess which one is the good one, try the longuest one or one with a prefix
                if opts.debug:
                    print(('opts.debug: ParseNormalCase: 2 matches: ({0}) and ({1})'.format(split1.group(0),
                                                                                            split11.group(0))))
                # first look for prefix like Tome+Vol to mark the "good" one
                # count non digit in splits
                c1 = 0
                for ch in split1.group(0):
                    if ch not in "0123456789 ":
                        c1 += 1
                c11 = 0
                for ch in split11.group(0):
                    if ch not in "0123456789 ":
                        c11 += 1
                # heuristic more non digit means more likely it is the central number
                if opts.debug:
                    print(('opts.debug: ParseNormalCase: 2 matches: take the longuest ({0},{1})'.format(c1, c11)))
                if c11 > c1:
                    split1 = split11

            if len(split1.groups()) == 1:
                # easy case
                if opts.debug:
                    print(('opts.debug: ParseNormalCase: {0}'.format(split1.groups())))
                self.parsed[0] = self.bdname[0:split1.start()]
                self.parsed[1] = split1.group('number')
                self.parsed[2] = self.bdname[split1.end():]
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print('ko 2 groups or more')
                return False, self.parsed

        if opts.debug:
            print('opts.debug: ParseNormalCase: split do not match normal number scheme')
        return False, self.parsed


class ParseNumberSerieTitle(ParserForNumber):
    """
    lookup for number sep serie sep title
    """
    def parse(self, hint_series=None):
        # different from \w
        words = '([A-z][A-z0-9]*)'
        regserie = r"""(?P<serie>{words}+(\s{words})*)""".format(words=words)
        regtitle = r"""(?P<title>{words}(\s{words})*)""".format(words=words)
        reg1 = re.compile(self.regnumber + regsep + regserie + regsep + regtitle + '[.]', re.VERBOSE)

        # search do not always work because of possible multiple matches
        split1 = reg1.search(self.bdname)

        # positive case, we have 1 match only
        if split1:
            l1 = len(split1.groups())
            if opts.debug:
                print(('opts.debug: ParseNumberSerieTitle: len={0} groups={1}'.format(l1, split1.group())))
                for i, n in enumerate(split1.groups()):
                    print(('opts.debug: ParseNumberSerieTitle: i={0} group={1}'.format(i, n)))
            if len(split1.groups()) == 9:
                # easy case
                self.parsed[0] = split1.group('serie')
                if len(self.parsed[0]) == 1 and self.parsed[0][0] in ('_', '-'):
                    # grrr this is another case
                    if opts.debug:
                        print(('opts.debug: ParseNumberSerieTitle: failed series cannot be: {0}'.format(self.parsed[0])))
                    return False, self.parsed
                self.parsed[1] = split1.group('number')
                self.parsed[2] = split1.group('title')+'.'+self.bdname[split1.end():]
                if len(self.parsed[2]) == 1 and self.parsed[2][0] in ('_', '-'):
                    # grrr this is another case
                    if opts.debug:
                        print(('opts.debug: ParseNumberSerieTitle: failed title cannot be: {0}'.format(self.parsed[2])))
                    return False, self.parsed
                if opts.debug:
                    print(('opts.debug: ParseNumberSerieTitle: serie={0} number={1} title={2}'.format(
                        self.parsed[0], self.parsed[1], self.parsed[2])))
                return True, self.parsed
            else:
                # two groups of number or more
                # to be dealt with later
                print('ko 2 groups or more')
                return False, self.parsed

        if opts.debug:
            print('opts.debug: ParseNumberSerieTitle: split do not match normal number scheme')
        return False, self.parsed


class ParseNoSerie(ParserForNumber):
    """
    lookup for this special synthax
    """
    def parse(self):
        # we do not find it: possibly we have no serie
        reg = re.compile(self.regtome + self.regnumber + regsep, re.VERBOSE)
        split = reg.search(self.bdname)

        # no serie
        if split:
            if len(split.groups()) == 1:
                self.parsed[1] = split.group('number')
                self.parsed[2] = self.bdname[split.end():]
                return True, self.parsed

        if opts.debug:
            print('opts.debug: ParseNoSerie: split do not match no serie')

        return False, self.parsed


class ParseNoTitle(ParserForNumber):
    """
    lookup for this special synthax
    """
    def parse(self):
        reg3 = re.compile(regsep + self.regtome + self.regnumber,  re.VERBOSE)
        split3 = reg3.search(self.bdname)

        # no title
        if split3:
            l3 = len(split3.groups())
            if l3 == 1:
                self.parsed[0] = self.bdname[0:split3.start()]
                self.parsed[1] = split3.group('number')
                self.parsed[2] = self.bdname[split3.end():]
                if opts.debug:
                    print('opts.debug: ParseNoTitle: ok')
                return True, self.parsed
            else:
                if opts.debug:
                    print(('opts.debug: ParseNoTitle: 1 != {0}'.format(l3)))

        if opts.debug:
            print('opts.debug: ParseNoTitle split do not match on no title')
        return False, self.parsed


class ParseNumberOnly(ParserForNumber):
    """
    lookup for this special synthax
    """
    def parse(self):
        reg3 = re.compile(self.regtome + self.regnumber,  re.VERBOSE)
        split3 = reg3.search(self.bdname)

        # no title
        if split3:
            l3 = len(split3.groups())
            if l3 == 1:
                self.parsed[0] = self.bdname[0:split3.start()]
                self.parsed[1] = split3.group('number')
                self.parsed[2] = self.bdname[split3.end():]
                if opts.debug:
                    print('opts.debug: ParseNumberOnly: ok')
                return True, self.parsed
            else:
                if opts.debug:
                    print(('opts.debug: ParseNumberOnly: 1 != {0}'.format(l3)))

        if opts.debug:
            print('opts.debug: ParseNumberOnly: split do not match on no title')
        return False, self.parsed


def normalize_number(bdname):
    """ look for number and return 3 parts before, number, after
    """
    parsed = ['', '', '']

    # try to eliminate some pattern wich complicate things later on
    # case of "1 of 3" at the end
    status, parsed = ParseSpecialOf(bdname).parse()
    if status:
        bdname = parsed[0]
        if opts.debug:
            print(('opts.debug: normalize_number: reduce bdname to {0}'.format(bdname)))
        # need to continue here, only partial match

    # try to eliminate some pattern wich complicate things later on
    # case: n # m
    status, parsed = ParseSpecial1(bdname).parse()
    if status:
        return parsed
    # case: 01#02
    status, parsed = ParseSpecial2(bdname).parse()
    if status:
        return parsed
    # case: HS01
    status, parsed = ParseSpecialHS(bdname).parse()
    if status:
        return parsed

    # normal cases
    status, parsed = ParseNormalCase(bdname).parse()
    if status:
        return parsed
    # try rare pattern longest first
    status, parsed = ParseNumberSerieTitle(bdname).parse()
    if status:
        return parsed
    # miss something?
    status, parsed = ParseNoTitle(bdname).parse()
    if status:
        return parsed
    # miss something?
    status, parsed = ParseNoSerie(bdname).parse()
    if status:
        return parsed
    # miss something?
    status, parsed = ParseNumberOnly(bdname).parse()
    if status:
        return parsed

    if opts.debug:
        print(('ko do not find a number in {0}'.format(bdname)))
    return parsed


def normalize_pre_number(text):
    """ parse pre number
    """
    parsed = ['']

    # look for common garbage
    # [BD FR]
    # BD.FR.
    # or a combinaison of above
    regbdfr1 = r"""\[?BD[\s.-]?[Ff][Rr]\]"""
    regbdfr2 = r"""BD[.]FR[.]"""
    regbdfr = r"""({0}(\s+{1})?)|({1}(\s+{0})?)""".format(regbdfr1, regbdfr2)
    reg1 = re.compile(regbdfr + regsep, re.VERBOSE)
    split1 = reg1.search(text)

    # good case
    if split1:
        end = split1.end()
        # remove some . if any
        while(text[end] in ('.', '-', ' ')):
            end = end+1
        parsed[0] = text[end:]
    else:
        parsed[0] = text

    # look for stopwords between () at end of text
    # ex:
    #   toto titi (le) -> le.toto.titi
    regparen = r"""[(](?P<stp>\w+)[)]"""
    reg2 = re.compile(regparen, re.IGNORECASE | re.VERBOSE)
    split2 = reg2.search(parsed[0])
    if split2:
        l2 = len(split2.groups())
        if l2 == 1 and split2.group('stp').lower() in stopwords:
            if opts.debug:
                print(('debug: normalize_pre_number: group={0}'.format(split2.groups())))
            # of we have found a stopwords at the (end)
            parsed[0] = split2.group('stp')+' '+parsed[0][:split2.start()-1]

    return parsed


def normalize_post_number(text):
    """
    parse post number i.e. title and suffix
    """
    regauthor = r"""\s*(?P<author>[(].+[)])"""
    regresolution = r"""\s*(?P<resolution>[\[].+[\]])"""
    regsuffix = r"""([.](?P<suffix>(pdf|cbz|cbr|zip|rar)))"""

    parsed = ['', '']

    # look for suffix
    reg1 = re.compile(regsuffix, re.VERBOSE)
    split1 = reg1.search(text)

    # good case
    if split1:
        parsed[0] = text[0:split1.start()]
        parsed[1] = split1.group('suffix')

    # look for author names or date in title
    reg2 = re.compile(regauthor+'|'+regresolution, re.VERBOSE)
    split2 = reg2.search(parsed[0])

    if split2:
        # remove author but not
        if opts.debug:
            print(('opts.debug: normalize_post_number: find author {0}'.format(split2.group('author'))))
            print(('opts.debug: normalize_post_number: parsed0 is {0}'.format(parsed[0])))
            print(('opts.debug: normalize_post_number: split2 is from {0} to {1}'.format(split2.start(), split2.end())))

        # if title is empty or it is the only information
        translation_table = dict.fromkeys(list(map(ord, '()-.[]{}')), None)
        parsed[0] = parsed[0].translate(translation_table)
#       if len(parsed[0]) > (split2.end()-split2.start()-1):
#          # remove leading and trailing .(\s
#          left_shift = 1
#          start = split2.start()
#          while((start-left_shift)>0 and parsed[0][start-left_shift] in ('.', '(', '-')):
#              left_shift = left_shift+1
#          parsed[0] = parsed[0][0:split2.start()-left_shift+1]
#       else:
#          parsed[0] = parsed[0][split2.start()+2:split2.end()-1]
    return parsed


def format_name(s):
    """proposed final name
    apply a few rules
    """

    result = ''

    # if we have a number
    if len(s[2]) > 0:

        result = s[0] + '/'

        # empty series
        if len(s[1]) == 0:
            result = result + s[0]
        else:
            result = result + s[1]

        # add number with a special case for HS
        if s[2][0:2].lower() == 'hs':
            result = result + '_HS' + s[2][2:]
        else:
            result = result + '_{:02d}'.format(int(s[2]))

        # add title if not empty
        if len(s[3]) > 0:
            # result = result + '_{:s}'.format(s[3])
            result = result + '_' + s[3]

        # add suffix
        result = result + '.' + s[4]

    return result


def normalize_file(text):
    """
    call normalize_file
    parse input and return a list with the different parts
    """
    (dirname, bookname) = os.path.split(text)

    if opts.debug:
        print('--------------------------------------------------')
    if opts.debug:
        print(('bookname = {0}'.format(bookname)))
    if opts.debug:
        print('--------------------------------------------------')

    # first call: trying to get number and split in 3
    parsed1 = normalize_number(bookname)
    if opts.debug:
        print(('ok parsenumber return [{0}], [{1}], [{2}]'.format(
            parsed1[0], parsed1[1], parsed1[2])))

    parsed2 = normalize_pre_number(parsed1[0])
    if opts.debug:
        print(('ok parsePreNumber return [{0}]'.format(
            parsed2[0])))

    parsed3 = normalize_post_number(parsed1[2])
    if opts.debug:
        print(('ok parsePostNumber return [{0}], [{1}]'.format(parsed3[0], parsed3[1])))

    # first is empty for now
    if opts.debug:
        print(('ok {0} pretty {1}'.format(parsed3[0], pretty(parsed3[0]))))
    return [dirname, pretty(parsed2[0]), parsed1[1], pretty(parsed3[0]), parsed3[1]]


def normalize_directory(current):
    """ normalize all files in a directory """
    regdir = '{:s}/*'.format(current)
    bdlist = glob.glob(regdir)
    for bd in bdlist:
        if os.path.isdir(bd):
            normalize_directory(bd)
        else:
            s = normalize_file(bd)
            if s:
                fs = format_name(s)
                if not fs or len(fs) == 0:
                    print(('echo KO {0}'.format(bd)))
                    continue
                if fs == bd:
                    if opts.debug:
                        print(('echo OK {0}'.format(bd)))
                else:
                    print(('echo OK {0} moved to {1}'.format(bd, fs)))
                    if opts.force:
                        os.rename(bd, fs)
            else:
                print(('normalize_file failed for {0}'.format(bd)))


# main
if __name__ == '__main__':

    opts = opts_parser.parse_args()

    # some traces
    if opts.debug:
        print(stopwords)

    # be careful with the locale
    # locale.setlocale(locale.LC_CTYPE,"fr_FR.UTF8")

    if os.path.isdir(opts.directory):
        # scan all files under dir, need to use a unicode regexp for glob
        normalize_directory(opts.directory)
    else:
        print(('{0} is not a directory'.format(opts.directory)))
        sys.exit(1)

    sys.exit(0)

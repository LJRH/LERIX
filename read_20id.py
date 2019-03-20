import re, os, time
import numpy as np
from numpy import array
from  dateutil.parser import parse as dateparse
from datetime import datetime

#path = '/Users/lukehiggins/OneDrive - University of Leeds/_HIGGINS-PhD_/__XAS__/__RAW-DATA__/20ID-APS/Standards/CarboxylicSilica'
#path = 'D:/DATA/XRS/20ID-APS/Other/CarboxylicSilica'
path = 'D:/DATA/XRS/20ID-APS/Nov2017/PyHTC-postMgOak-250+450'
widedat = path + '/' + 'nixs.0001'

COMMENTCHARS = '#;%*!$'
NAME_MATCH = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$").match
VALID_SNAME_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
VALID_NAME_CHARS = '.%s' % VALID_SNAME_CHARS
RESERVED_WORDS = ('and', 'as', 'assert', 'break', 'class', 'continue',
                'def', 'del', 'elif', 'else', 'eval', 'except', 'exec',
                'execfile', 'finally', 'for', 'from', 'global', 'if',
                'import', 'in', 'is', 'lambda', 'not', 'or', 'pass',
                'print', 'raise', 'return', 'try', 'while', 'with',
                'group', 'end', 'endwhile', 'endif', 'endfor', 'endtry',
                'enddef', 'True', 'False', 'None')

def getfloats(txt, allow_times=True):
    """
    function goes through a line and returns the line as a list of strings
    """
    words = [w.strip() for w in txt.replace(',', ' ').split()]
    mktime = time.mktime
    for i, w in enumerate(words):
        val = None
        try:
            val = float(w)
        except ValueError:
            try:
                val = mktime(dateparse(w).timetuple())
            except ValueError:
                pass
    words[i] = val
    return(words)

def colname(txt):
    return fixName(txt.strip().lower()).replace('.', '_')

def isValidName(filename):
    if filename in RESERVED_WORDS:
        return False
    tnam = filename[:].lower()
    return NAME_MATCH(tnam) is not None

def fixName(filename, allow_dot=True):
    if isValidName(filename):
        return filename
    if isValidName('_%s' % filename):
        return '_%s' % filename
    chars = []
    valid_chars = VALID_SNAME_CHARS
    if allow_dot:
        valid_chars = VALID_NAME_CHARS
    for s in filename:
        if s not in valid_chars:
            s = '_'
        chars.append(s)
    filename = ''.join(chars)
    # last check (name may begin with a number or .)
    if not isValidName(filename):
        filename = '_%s' % filename
    return filename

def strip_headers(headers):
    #reorganise the headers and remove superfluous lines and commentchars
    header = []
    for hline in headers:
        hline = hline.strip().replace('\t', ' ')
        if len(hline) < 1:
            continue
        if hline[0] in COMMENTCHARS:
            hline = hline[1:].lstrip() #assumes reading l2r
        if len(hline) <1:
            continue
        header.append(hline)
    return(header)

def separate_infile(text):
    _labelline = None
    ncol = None
    dat, footers, headers = [], [], []
    text.reverse()
    section = 'FOOTER'
    for line in text:
        line = line.strip()
        if len(line) < 1: #remove any blank lines
            continue
        if section == 'FOOTER' and not None in getfloats(line):
            section = 'DATA'
        elif section == 'DATA' and None in getfloats(line):
            section = 'HEADER'
            _labelline = line
            if _labelline[0] in COMMENTCHARS:
                _labelline = _labelline[1:].strip()
        if section == 'FOOTER': #reading footers but not using them currently
            footers.append(line)
        elif section == 'HEADER':
            headers.append(line)
        elif section == 'DATA':
            rowdat  = getfloats(line)
            if ncol is None:
                ncol = len(rowdat)
            if ncol == len(rowdat):
                dat.append(rowdat)
    return(headers, dat, footers)

def pull_id20attrs(header):
    bounds, steps, int_times = [], [], []
    header_attrs = {}
    line = -2
    #iterate through the header and pull out useful information and send it to header_attrs Dictionary
    for hhline in map(str.lower,header):
        line = line + 1 #counting to return the user comments which are on the next line
        try:
            if str(header[comment_line].strip()) == 'Scan config:':
                header_attrs['User Comments'] = ""
                pass
            else:
                header_attrs['User Comments'] = str(header[comment_line].strip())
        except:
            pass
        if hhline.startswith('beamline'):
            words = hhline.split('beamline',1)
            header_attrs['beamline'] = str(words[1].strip())
        elif hhline.startswith('e0'):
            if ':' in hhline:
                words = hhline.split(':',1)
                header_attrs[words[0]] = float(words[1].strip(' ').split(' ',1)[0])
            elif '=' in hhline:
                words = hhline.split('=',1)
                header_attrs[words[0]] = float(words[1].strip(' ').split(' ',1)[0])
        elif hhline.startswith('user comment'):
            comment_line = line
        elif "scan time" in hhline:
            #search for scan date and time see: https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            try:
                words = hhline.split('scan time',1)
                header_attrs['scan_time'] = datetime.strptime(words[1].strip(), '%H hrs %M min %S sec.').time()
                header_attrs['scan_date'] = datetime.strptime(words[0].split('panel',1)[1].strip().strip(';'), '%m/%d/%Y  %I:%M:%S %p').date()
            except:
                continue
        elif "scan bounds" in hhline:
            words = hhline.split('scan bounds',1)
            for i in words[1].strip(':').split(' '):
                try:
                    bounds.append(float(i))
                except:
                    pass
            header_attrs['scan_bounds'] = bounds
        elif "scan step(s)" in hhline:
            words = hhline.split('scan step(s)',1)
            for i in words[1].strip(':').split(' '):
                try:
                    steps.append(float(i))
                except:
                    pass
            header_attrs['scan_steps'] = steps
        elif "integration times" in hhline:
            words = hhline.split('integration times',1)
            for i in words[1].strip(':').split(' '):
                try:
                    int_times.append(float(i))
                except:
                    pass
            header_attrs['int_times'] = int_times
    return(header_attrs)

def get_col_headers(header):
    col_headers = []
    for i in colname(header[0]).split('___'): #need three _ to work
        if not i:
            continue
        col_headers.append(i.strip('_'))
    return(col_headers)

def read_20ID(file):
    f = open(file, "r") #read starts here
    text = f.read()
    text = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    data = {}
    headers, dat, footers = separate_infile(text)
    try:
        dat = [map(list,zip(*dat))[i][::-1] for i in range(len(dat[1]))] # this function does the inverse ([::-1]) transposition of the dat object, doesn't seem to work in windows
    except:
        dat = [list(map(list,zip(*dat)))[i][::-1] for i in range(len(dat[1]))]
    dat = np.array(dat,dtype='float64')
    for i in range(len(dat)):
        data[get_col_headers(strip_headers(headers))[i]] = dat[i]
    header_attrs = pull_id20attrs(strip_headers(headers))
    return(data, header_attrs)

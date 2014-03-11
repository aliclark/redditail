#!/usr/bin/python

import sys, re, time, HTMLParser, termcolor, codecs, datetime

sys.stdin = codecs.getreader('utf-8')(sys.stdin)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

h = HTMLParser.HTMLParser()

# In practice, 5 digit numbers are common
upsmax = 5
def upsmax_update(n):
    global upsmax
    l = len(n)
    if l > upsmax:
        upsmax = l

def upspad(n):
    upsmax_update(n)
    return n.rjust(upsmax)

def upsstr(u):
    return upspad(str(u))

def mkline(created_utc, ups, downs, title, permalink, domain):
    ups = int(ups)
    downs = int(downs)
    score = str(int(round((ups * 10.) / (ups + downs))))
    if score == '10':
        score = '+'

    return termcolor.colored(time.strftime("%H:%M", time.localtime(int(float(created_utc)))), 'white') + ' ' + termcolor.colored(upsstr(ups), 'green') + ' ' + termcolor.colored(score, 'yellow') + ' ' + h.unescape(title) + ' ' + termcolor.colored('https://pay.reddit.com' + permalink, 'cyan') + ' ' + termcolor.colored(domain, 'yellow') + '\n'

def info(x):
    sys.stderr.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + ' INFO  ' + str(x) + '\n')

splitter = re.compile(r"^(?P<created_utc>[^\t]+)\t(?P<ups>[^\t]+)\t(?P<downs>[^\t]+)\t(?P<title>[^\t]+)\t(?P<permalink>[^\t]+)\t(?P<domain>[^\t\n]+)$")

def main():
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            m = splitter.match(line)
            if m:
                result = mkline(m.group('created_utc'), m.group('ups'), m.group('downs'), m.group('title'), m.group('permalink'), m.group('domain'))
                if result:
                    line = result
            sys.stdout.write(line)
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

#!/usr/bin/python

import sys, errno, os, os.path, urllib2, json, time, string, socket, codecs, datetime

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

"""
* **Make no more than thirty requests per minute.** This allows some burstiness
  to your requests, but keep it sane. On average, we should see no more than
  one request every two seconds from you.
* Change your client's User-Agent string to something unique and descriptive,
  preferably referencing your reddit username.
    * Example: `User-Agent: flairbot/1.0 by spladug`
    * Many default User-Agents (like "Python/urllib" or "Java") are drastically
      limited to encourage unique and descriptive user-agent strings.
    * If you're making an application for others to use, please include a
      version number in the user agent. This allows us to block buggy versions
      without blocking all versions of your app.
    * **NEVER lie about your user-agent.** This includes spoofing popular
      browsers and spoofing other bots. We will ban liars with extreme
      prejudice.
* Most pages are cached for 30 seconds, so you won't get fresh data if you
  request the same page that often. Don't hit the same page more than once
  per 30 seconds.
* Requests for multiple resources at a time are always better than requests for
  single-resources in a loop. Talk to us on the mailing list or in #reddit-dev
  if we don't have a batch API for what you're trying to do.
* Our robots.txt is for search engines not API clients. Obey these rules for
  API clients instead.
"""

fields = None

def children(j):
    rv = []
    for ch in j['data']['children']:
        rv.append(ch['data'])
    return rv

def trylookup(item, default, field):
    if field in item:
        return item[field]
    return default

def itemstring(item):
    return '\t'.join(map(lambda field: unicode(trylookup(item, '', field)), fields)) + '\n'

def textify(ch):
    s = ''
    for c in ch:
        s += itemstring(c)
    return s

def info(x):
    sys.stderr.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + ' INFO  ' + str(x) + '\n')

def decommentize(s):
    commentstart = s.find('#')
    if commentstart >= 0:
        return s[:commentstart]
    return s

def read_reddits(f):
    return [s for s in map(string.strip, map(decommentize, f.read().split('\n'))) if s != '']

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def main():
    global fields

    # TODO: put this in a config file
    fields = ['created_utc', 'ups', 'downs', 'title', 'permalink', 'domain']

    logf = None
    titles = set([])

    # it can take time when busy
    timeout_secs = 16

    # Rule 1 & 3 - (be careful not to stop and start within this time
    # though, TODO: save 'lastcall' timestamp in dotfile)
    sleep_time = 30

    mkdir_p(os.path.expanduser("~/.redditail"))
    seenfilepath = os.path.expanduser("~/.redditail/seen")

    try:
        logf = open(seenfilepath, 'r')
        for line in logf:
            titles.add(line.decode('utf8')[:-1])
        close(logf)
    except:
        pass

    logf = open(seenfilepath, 'a')

    reddits_string = '+'.join(sorted(map(urllib2.quote, set(map(string.lower, read_reddits(sys.stdin))))))

    # Rule 2
    user_agent = 'redditail/1.0 by redditail'

    headers = { 'User-Agent' : user_agent }

    try:
        while True:
            url = 'http://api.reddit.com/r/' + reddits_string + '/hot.json?limit=100'

            info('GET  ' + url)
            req = urllib2.Request(url, None, headers)
            try:
                response = urllib2.urlopen(req, timeout=timeout_secs)
                data = response.read()
                info('content-length: ' + response.info().getheader('content-length'))

                j = json.loads(data)

                ch = children(j)
                chnew = []

                for c in ch:
                    # Some reddits have very low "hot" threshold,
                    # presumably because items rarely get upvotes.
                    # If it gets another upvote, will show it later
                    if c['ups'] <= 1:
                        continue

                    # filter out reposts from the batch, showing the earlier one only
                    for c2 in ch:
                        if (((c2['title'] in c['title']) or (c['title'] in c2['title'])) and
                            (int(c['id'], 36) > int(c2['id'], 36))):
                            # c is a repost of c2
                            break
                    else:
                        # if we've already seen a similar title, ignore this one.
                        for t in titles:
                            if (c['title'] in t) or (t in c['title']):
                                break
                        else:
                            titles.add(c['title'])
                            chnew.append(c)
                            if logf:
                                logf.write(c['title'].encode('utf8') + '\n')
                                logf.flush()

                sys.stdout.write(textify(sorted(chnew, key=lambda x: x['created_utc'])))
                sys.stdout.flush()

            except socket.error, e:
                info(e)
            except urllib2.URLError, e:
                info(e)
            except urllib2.HTTPError, e:
                info(e)

            time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

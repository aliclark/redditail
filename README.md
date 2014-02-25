redditail
=========

Like tail -f but for reddit

```sh
./redditail.py <subreddits.list
```

Where subreddits.list contains a list of subreddits with blank lines
and anything past a # character ignored.

This will display the top 100 "hot" page, excluding any titles that
are substrings of ones already seen (saved to ~/.redditail/seen).

The script rechecks every 30 seconds and prints out any new entries to
the hot list.

The first number displayed is the number of upvotes, the second is the
proportion of upvotes to downotes out of 10, with + indicating 10/10.

eg. for subreddits.list:

```
# Tech subreddits
programming
opensource
techsnap
# and so on

# Music subreddits
truemusic
listentous
# etc.
```

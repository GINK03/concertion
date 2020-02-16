from collections import namedtuple

DayAndPath = namedtuple('DayAndPath', ['day', 'path'])

DataType = namedtuple('DataType', ['data', 'type'])

TitleUrlDigestScore = namedtuple('TitleUrlDigestScore', ['title', 'url', 'digest', 'score', 'date', 'category'])

YJComment = namedtuple('YJComment', ['username', 'comment', 'good', 'bad', 'urls', 'parent_digest', 'ts'])

Hot5ch = namedtuple('Hot5ch', ['digest', 'ts', 'url', 'text', 'num', 'html'])

# -*- coding: utf-8 -*-
from queue import Queue
import json
import sys
import requests

URL = 'https://ja.wikipedia.org/w/api.php'


def get_link(title, plcontinue=None):
    params = {
        'format': 'json',
        'action': 'query',
        'prop': 'links',
        'redirects': '',
        'pllimit': 500,
        'plnamespace': 0,
        'titles': title,
        'plcontinue': plcontinue,
    }
    return json.loads(requests.get(url=URL, params=params).text)


def get_fulltitle(title):
    params = {
        'format': 'json',
        'action': 'query',
        'redirects': '',
        'titles': title,
    }
    return json.loads(requests.get(url=URL, params=params).text)


def get_nodes(title):
    titles = []
    ret = get_link(title)
    while 1:
        pages = ret['query']['pages'].values()
        titles += [links['title'] for items in pages
                   for links in items['links']]
        if 'continue' in ret:
            ret = get_link(title, ret['continue']['plcontinue'])
        else:
            break

    return titles


def get_items(ret):
    pages = ret['query']['pages'].values()
    items = {key: items[key] for items in pages for key in items}
    return items


def search(start, goal):
    print('search start %s -> %s' % (start, goal))
    que = Queue()
    que.put(start)
    parent = {start: None}
    res = []

    while not que.empty():
        key = que.get()
        print(key)
        nodes = get_nodes(key)

        for node in nodes:
            if node not in parent:
                parent[node] = key
                que.put(node)

        if goal in nodes:
            res.append(goal)
            key = goal
            while 1:
                key = parent[key]
                if not key:
                    break
                res.append(key)
            break

    return res


def main(start, goal):
    f_start = get_items(get_fulltitle(start))
    if 'missing' in f_start:
        print('%s not found' % start)
        return 1
    f_goal = get_items(get_fulltitle(goal))
    if 'missing' in f_goal:
        print('%s not found' % goal)
        return 1

    res = search(f_start['title'], f_goal['title'])

    print('---------result---------')
    for w in reversed(res):
        print(w)


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print('Usage: python %s [from] [to]' % sys.argv[0])
        sys.exit(1)
    main(start=sys.argv[1], goal=sys.argv[2])

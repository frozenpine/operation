# -*- coding: UTF-8 -*-
from lxml.etree import parse


def etree_to_dict(t):
    d = {t.tag: map(etree_to_dict, t.iterchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['text'] = t.text
    return d


def xmlloader(f):
    return etree_to_dict(parse(f).getroot())

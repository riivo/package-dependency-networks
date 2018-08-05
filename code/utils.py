import calendar

import pytz
from dateutil.parser import parse


def parse_date(datestr):
    d = parse(datestr)
    in_utc = d.astimezone(pytz.utc)
    naive = in_utc.replace(tzinfo=None)
    return calendar.timegm(naive.timetuple())


def parse_date_naive(datestr):
    """
    If no timezone, assumes UTC
    :param datestr:
    :return:
    """

    d = parse(datestr)
    if d.tzinfo is None:
        naive = d.replace(tzinfo=None)
    else:
        in_utc = d.astimezone(pytz.utc)
        naive = in_utc.replace(tzinfo=None)
    return calendar.timegm(naive.timetuple())

def fix_semantic_x(ver_):
    ver = ver_.strip("'").strip()
    ver = ver.replace("git", "*").replace("latest", "*").replace("path", "*").replace(" ", "").replace("X",
                                                                                                       "x").replace(
        "\t", "")

    """
    if ver.find("http") != -1:
        return "*"
    if ver.find(".com") != -1:
        return "*"
    """
    # emtpty is wildcard, x is wildcard in javascript
    if ver == "" or ver == "x":
        ver = "*"  # FIXME should we (does it hold for ruby, rust, js etc)
        return ver

    # "~1" is eq ">=1.0.0,<2.0.0" etc
    if len(ver) == 2 and ver[0] == "~" and ver[1].isdigit():
        digit = int(ver[1])
        return ">={0}.0.0,<{1}.0.0".format(digit, digit + 1)

    if ver[0:2] == "~>":  # Ruby ~>0.2 is equivalent to >=0.2,<1
        remaining = ver[2:]
        pointpos = remaining.rfind(".")
        removed = remaining[:pointpos]

        pointpos = removed.rfind(".")
        if pointpos == -1:
            return ">={0},<{1}".format(remaining, int(removed) + 1)
        else:
            lastrange = int(removed[pointpos + 1:])
            return ">={0},<{1}.{2}".format(remaining, removed[:pointpos], lastrange + 1)

    ver = ver.replace(".*.*", ".*")
    # Rust 0.3.* is equivalent to >=0.3,<0.4
    if ver[0].isdigit() and ver[-2:] == ".*":
        ver_ = ver[:-2]
        pointpos = ver_.rfind(".")

        if pointpos == -1:  # 0.* case
            intver = int(ver_)
            return ">={0},<{1}".format(intver, intver + 1)
        else:  # 0.a.a.* case
            lastrange = int(ver_[pointpos + 1:])
            return ">={0}.{1},<{0}.{2}".format(ver_[:pointpos], lastrange, lastrange + 1)

    pos = ver.find(".x")

    if pos == -1:
        return ver

    if pos != -1:
        ver = ver[:pos]
        ver = ver.replace("~", "")  # does not matter and bug in semantic_version library

    ver = ver.strip()
    if ver == "x":
        ver = "*"

    return ver  # does not like spaces


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def flatten(arr):
    res = []
    for x in arr:
        res.extend(x)
    return res

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""tagcat is a kittie who loves audiofiles.

Coretags
===
- ARTIST
- ALBUMARTIST
- TITLE
- TRACKNUMBER
- DISCMUMBER*

"""


import os
import argparse
import taglib
import re


BASEDIR = "/home/music/test"
CLEANTAGS = ["ARTIST",
             "ALBUMARTIST",
             "ALBUM",
             "DISCNUMBER",
             "TRACKNUNMBER",
             "TITLE",
             "BPM",
             "CATALOGNUMBER",
             "PUBLISHER",
             "LABEL"]


def main():
    """This is main, not sparta!
    """

    if len(os.sys.argv) <= 2:
        help()
        raise AttributeError

    jmp = os.sys.argv[1]
    argv = os.sys.argv[2:]

    if jmp == "list" or jmp == "ls":
        tc_list(argv)

    elif jmp == "write" or jmp == "wr":
        tc_write(argv)

    elif jmp == "delete" or jmp == "del":
        tc_delete(argv)

    elif jmp == "wipeout" or jmp == "wo":
        tc_wipeout(argv)

    elif jmp == "clear" or jmp == "cl":
        tc_clear(argv)

    else:
        raise ValueError


def help():
    """Prints the main help for tagcat.
    """
    s = "usage: tagcat [list|write|swipe|delete|clear|rename] ..."

    print(s)


def filewalk(ls, recursiv=False, test=os.path.isfile):
    """Finds valid files from a list of path.  Valid files are defined by the
    test function.  If an item of the given list is a directorie and recursiv
    is set True, filewalk finds valid files recursively in that directorie.

    helllo

    Args:
        ls: A list of files/directories.  ``list[str]``
        recursiv: Find files recursivly.  ``bool``
        test: A function to test against each file/string.  ``func``

    Returns:
        list: A list of absolute filenames that passes ``test``.

    Raises:
        TypeError:  If an argument has not an excepted instance.

    """

    if not isinstance(ls, list):
        raise TypeError("``ls`` is not a ``list``")

    if not isinstance(recursiv, bool):
        raise TypeError("``recursiv`` is not a ``bool``")

    if not callable(test):
        raise TypeError("``test`` is not a ``function``")

    def recursion(index, retval):
        # pylint: disable=unused-variable

        # basecase
        if index == len(ls):
            return retval

        # do something with `ls[index]` and `retval`
        if recursiv and os.path.isdir(ls[index]):
            for root, dirs, files in os.walk(ls[index]):
                for fn in files:
                    ls.append(os.path.join(root, fn))
        else:
            if test(ls[index]):
                retval.append(os.path.abspath(ls[index]))

        # recusrion
        return recursion(index+1, retval)

    # start and set default values for `index` and `retval`
    return recursion(0, [])


def isaudio(fn):
    """Test if `fn` is a valid audiofile.

    Args:
        fn: A filename.

    Returns:
        bool: True if `fn` is a audiofile, False otherwise.

    Raises:
        ValueType: If `fn` is not an instance from `str`.

    """

    if not isinstance(fn, str):
        raise TypeError("``fn`` is not a ``str``")

    if not os.path.isfile(fn):
        return False

    elif os.path.isfile(fn) and os.path.islink(fn):
        return False

    elif not fn.endswith((".mp3", ".MP3", ".flac", ".FLAC")):
        return False

    return True


def read_tags(fn):
    """Reads tags from an audio file.

    Returns:
        dict: A dictinary with the tag, value pairs.

    Raises:
        TypeError: If ``fn`` is not a ``str``

    """

    try:
        afile = taglib.File(fn)
        tags = afile.tags
        info = {"path": [afile.path],
                "samplerate": [str(afile.sampleRate)],
                "lenght": [str(afile.length)],
                "bitrate": [str(afile.bitrate)],
                "channels": [str(afile.channels)]}
        tags.update(info)
        afile.close()
    except OSError:
        tags = {}

    return tags


def merge_tags(ls):
    """Merges all tags together in one dict.
    """

    if not isinstance(ls, list):
        raise TypeError("``ls`` is not an instance from ``list``")

    if len(ls) == 0:
        return {}

    def recursion(index, retval, memo):

        # basecase
        if index >= len(ls):
            return retval

        # do stuff to retval and memo
        tags = read_tags(ls[index])
        for tag in set(list(retval.keys()) + list(tags.keys())) - set(memo):
            try:
                if retval[tag] != tags[tag]:
                    raise KeyError
            except KeyError:
                retval[tag] = ["~"]
                memo.append(tag)

        # recursion
        return recursion(index+1, retval, memo)

    # start recursion and set default values
    return recursion(1, read_tags(ls[0]), [])


def print_tags(tags):
    """Prints tags to stdout
    """
    l = 0
    for k in tags.keys():
        if len(k) > l:
            l = len(k)

    s = ""
    for tag in sorted(tags):
        s += "{0:{1}}: `{2}`\n".format(tag.lower(), l+1, ", ".join(tags[tag]))
    print(s)


def tc_list(argv):
    """
    """

    parser = argparse.ArgumentParser(prog="tagcat [list|ls]")
    parser.add_argument("files", metavar="FILE", nargs="+")
    parser.add_argument("-r", "--recursiv", action="store_true")
    args = parser.parse_args(argv)

    files = filewalk(args.files, recursiv=args.recursiv, test=isaudio)
    tags = merge_tags(files)
    print_tags(tags)


def tc_write(argv):
    """Parses arguments from commandline and runs write_tags.
    """
    parser = argparse.ArgumentParser(prog="tagcat [write|wr]")
    parser.add_argument("files", metavar="FILE", nargs="+")
    parser.add_argument("-r", "--recursiv", action="store_true")
    parser.add_argument("-a", "--artist")
    parser.add_argument("-aa", "--albumartist")
    parser.add_argument("-A", "--album")
    parser.add_argument("-t", "--title")
    parser.add_argument("-n", "--tracknumber")
    parser.add_argument("-l", "--label")
    parser.add_argument("-b", "--bpm")
    # parser.add_argument("-c", "--catalognumber")
    parser.add_argument("-g", "--genre")
    parser.add_argument("-s", "--style")
    parser.add_argument("-c", "--comment")

    tags = vars(parser.parse_args(argv))

    recursiv = tags.pop("recursiv")
    files = filewalk(tags.pop("files"), recursiv=recursiv, test=isaudio)

    write_tags(files, tags)


def write_tags(ls, tags):
    """Writes tags to an audiofile.
    """

    def recursion(index):

        if index == len(ls):
            return

        af = taglib.File(ls[index])
        for t, v in tags.items():
            if v:
                af.tags[t.upper()] = [v]

        af.save()
        af.close()

        return recursion(index+1)

    return recursion(0)


def del_tags(ls, tags):
    """Deletes tags form audiofiles.
    """

    def recursion(index):

        if index == len(ls):
            return

        af = taglib.File(ls[index])
        for t in tags:
            if t.upper() in af.tags:
                del af.tags[t.upper()]
        af.save()
        af.close()

        return recursion(index+1)

    return recursion(0)


def tc_delete(argv):
    """Parses cmd arguments and runs del_tags()

    Usage:
        tagcat delete -r -t artist album -- testfiles/

    """

    parser = argparse.ArgumentParser(prog="tagcat [delete|del]")
    parser.add_argument("files", metavar="FILE", nargs="+")
    parser.add_argument("-r", "--recursiv", action="store_true")
    parser.add_argument("-t", "--tags", dest="tags", nargs="+")

    args = parser.parse_args(argv)

    filelist = filewalk(args.files, recursiv=args.recursiv, test=isaudio)
    del_tags(filelist, args.tags)


def wipeout_tags(ls):
    """Removes all tags from audiofiles.
    """

    if not isinstance(ls, list):
        raise TypeError("``ls`` is not an instance of ``list``")

    if len(ls) == 0:
        return

    def recursion(index):

        if index == len(ls):
            return

        af = taglib.File(ls[index])
        af.tags.clear()
        af.removeUnsupportedProperties(af.unsupported)  # not sure
        af.save()
        af.close()

        return recursion(index+1)

    return recursion(0)


def tc_wipeout(argv):
    """Parses cmd arguments and run wipeout_tags.
    """

    parser = argparse.ArgumentParser(prog="tagcat [wipeout|wo]")
    parser.add_argument("files", metavar="FILE", nargs="+")
    parser.add_argument("-r", "--recursiv", action="store_true")

    args = parser.parse_args(argv)

    filelist = filewalk(args.files, recursiv=args.recursiv, test=isaudio)
    wipeout_tags(filelist)


def clear_tags(ls):
    """Removes all multiply tag values and strip whitspaces from the first.
    """

    if not isinstance(ls, list):
        raise TypeError

    if len(ls) == 0:
        raise ValueError

    def recursion(index):

        if index == len(ls):
            return

        af = taglib.File(ls[index])
        for t in list(af.tags.keys()):
            if t in CLEANTAGS:
                af.tags[t] = [af.tags[t][:1][0].strip()]
            else:
                del af.tags[t]
        af.save()
        af.close()

        return recursion(index+1)

    return recursion(0)


def tc_clear(argv):
    """
    """

    parser = argparse.ArgumentParser(prog="tagcat [clear|cl]")
    parser.add_argument("files", metavar="FILE", nargs="+")
    parser.add_argument("-r", "--recursiv", action="store_true")

    args = parser.parse_args(argv)

    filelist = filewalk(args.files, recursiv=args.recursiv, test=isaudio)
    clear_tags(filelist)


def generate_path(ls):
    """Generates a new filename and path.
    """

    if not isinstance(ls, list):
        raise TypeError

    if len(ls) == 0:
        raise ValueError

    def recursion(index, retval):

        if index == len(ls):
            return retval

        # do stuff

        return recursion(index+1, retval)

    return recursion(0, [])


def gen_path(fn):
    """Generates a new filename.
    """

    if not isinstance(fn, str):
        raise TypeError

    af = taglib.File(fn)

    try:
        artist = af.tags["ARTIST"]
        album = af.tags["ALBUM"]
        albumartist = af.tags["ALBUMARTIST"]
        title = af.tags["TITLE"]
        tracknumber = af.tags["TRACKNUNMBER"]
    except KeyError:
        raise ValueError("`{0}` needs more tags")

    af.close()


def tagval_mutation(s):
    """Mutates the tag value to an filesystem friendly version.

    1. translate to lowercase
    2. translate unicode chrs to ascii chrs
    3. remove all unwanted/unknown chrs ^[a-z0-9-.&]
    4. strip whitespaces
    5. remove double whitespaces
    6. replaces whitespaces whit underscores

    """

    # (1) translate to lowercase
    s = s.lower()
    # (2) translate unicode chrs
    s = translate_ascii(s)
    # (3)
    nonascii = re.compile("[^-a-z0-9_\.\ \(\)]")
    s = nonascii.sub("", s)
    # (4) strip whitespaces
    s = s.strip()
    # (5 + 6) remove/replace whitspaces (6., 7.)
    whitespaces = re.compile("\s+")
    s = whitespaces.sub("_", s)

    print(s)


def translate_unicode(string):
    """Translate a string to ascii character only (hopefully).

    Args:
        string: A string to substitute.

    returns:
        string: A string whitout any non ascii characters.

    """

    table = {ord("ß"): "sz",
             # a
             ord("ä"): "ae",
             ord("æ"): "ae",
             ord("à"): "a",
             ord("á"): "a",
             ord("â"): "a",
             ord("ã"): "a",
             ord("å"): "a",
             # e
             ord("è"): "e",
             ord("é"): "e",
             ord("ê"): "e",
             ord("ë"): "e",
             # i
             ord("ì"): "i",
             ord("í"): "i",
             ord("î"): "i",
             ord("ï"): "i",
             # n
             ord("ñ"): "n",
             ord("ņ"): "n",
             ord("ň"): "n",
             ord("ŉ"): "n",
             ord("ŋ"): "n",
             # o
             ord("ö"): "oe",
             ord("ò"): "o",
             ord("ó"): "o",
             ord("ô"): "o",
             ord("õ"): "o",
             ord("ø"): "o",
             ord("õ"): "o",
             ord("ō"): "o",
             ord("ő"): "o",
             ord("ǒ"): "o",
             ord("ȱ"): "o",
             # r
             ord("ŕ"): "r",
             ord("ŗ"): "r",
             ord("ř"): "r",
             # s
             ord("ś"): "s",
             ord("ŝ"): "s",
             ord("ş"): "s",
             ord("š"): "s",
             ord("ś"): "s",
             # c
             ord("ć"): "c",
             ord("ĉ"): "c",
             ord("ċ"): "c",
             ord("č"): "c",
             # u
             ord("ü"): "ue",
             ord("ù"): "u",
             ord("ú"): "u",
             ord("û"): "u",
             ord("ů"): "u",
             ord("ũ"): "u",
             ord("ũ"): "u",
             ord("ŭ"): "u",
             ord("ű"): "u",
             ord("ų"): "u",
             }

    return string.translate(table)


def samedir(ls):
    """Test if all files are in the same directorie.

    Args:
        fl: A list of absolute filenames.

    Returns:
        bool

    Raises:
        ...

    """

    if not isinstance(ls, list):
        raise TypeError

    if len(ls) == 0:
        raise ValueError

    def recursion(index):

        if index == len(ls) or len(ls) == 1:
            return True

        if os.path.dirname(ls[index]) != os.path.dirname(ls[0]):
            return False

        return recursion(index+1)

    return recursion(1)


def has_coretags(fh):
    """Test if the file contain all core tags.

    Args:
        fh: A taglib.File instance.

    Returns:
        bool: Wether the file has all core tags or not.

    Raises:
        ...

    """

    if not isinstance(fh, taglib.File):
        raise TypeError

    if all(k in fh.tags for k in ("ARTIST",
                                  "ALBUMARTIST",
                                  "ALBUM",
                                  "TITLE",
                                  "TRACKNUMBER")):
        return True

    return False


def read_coretags(fn):
    """
    """

    tags = read_tags(fn)

    if not has_coretags(tags):
        return

    return tags


def gen_filename(fn):
    """Generates the file name based on the tag data.

    Description:
        * open the file with taglib.File()
        * test for needed tags
        * read out tracknumber as int
        * read out totaltracks as int
        * read out discnumber as int
        *

    """

    if not isinstance(fn, str):
        raise TypeError

    fh = taglib.File(fn)
    tags = fh.tags

    if not has_coretags(tags):
        raise ValueError("no coretags")

    tracknr = fh.tags["TRACKNUMBER"]
    disc = fh.tags["DISCNUMBER"]
    artist = tagval_mutation(fh.tags["ARTIST"])
    title = tagval_mutation(fh.tags["TITLE"])
    album = tagval_mutation(fh.tags["ALBUM"])
    albumartist = tagval_mutation(fh.tags["ALBUMARTIST"])
    ending = os.path.splitext(fn)[1]

    filename = "{0}-{1}-{2}.{3}".format(tracknr, artist, title, ending)
    dirname = os.path.join(BASEDIR, albumartist, album, disc)

    return os.path.normpath(os.path.join(dirname, filename))


def rename(ls):
    """Renames an audiofile based on its tags.

    Args:
        ls: A list of filenames.

    Returns:
        None

    Raises:
        ...

    """

    if not isinstance(ls, list):
        raise TypeError

    def recursion(index):

        # end recursion
        if index == len(ls):
            return None

        # do stuff
        fn = ls[index]
        dest = gen_filename(fn)

        if os.path.exists(dest):
            raise NotImplementedError

        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))

        os.rename(fn, dest)

        # the recursion
        return recursion(index+1)

    # start recursion and default values
    return recursion(0)


if __name__ == "__main__":
    main()

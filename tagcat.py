#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring


import os
import argparse
import taglib


def main():
    """This is main, not sparta!
    """

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

    else:
        raise ValueError


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
        s += "{0:{1}}: {2}\n".format(tag.lower(), l+1, ", ".join(tags[tag]))
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


if __name__ == "__main__":
    main()

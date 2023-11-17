import argparse
import sys
import filecmp
import os
import re
import itertools
from difflib import Differ, SequenceMatcher

class POSIXDiffer(Differ):
    """
    This class produces differences in the POSIX default format 
    (see http://www.unix.com/man-page/POSIX/1posix/diff/),
    which is the same as the Gnu diff "normal format"
    (see http://www.gnu.org/software/diffutils/manual/diffutils.html#Normal).
    """

    def compare(self, a, b):
        cruncher = SequenceMatcher(self.linejunk, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if alo == ahi:
                f1 = '%d' % alo
            elif alo+1 == ahi:
                f1 = '%d' % (alo+1)
            else:
                f1 = '%d,%d' % (alo+1, ahi)

            if blo == bhi:
                f2 = '%d' % blo
            elif blo+1 == bhi:
                f2 = '%d' % (blo+1)
            else:
                f2 = '%d,%d' % (blo+1, bhi)

            if tag == 'replace':
                g = itertools.chain([ '%sc%s\n' % (f1, f2) ], self._my_plain_replace(a, alo, ahi, b, blo, bhi))
            elif tag == 'delete':
                g = itertools.chain([ '%sd%s\n' % (f1, f2) ], self._dump('<', a, alo, ahi))
            elif tag == 'insert':
                g = itertools.chain([ '%sa%s\n' % (f1, f2) ], self._dump('>', b, blo, bhi))
            elif tag == 'equal':
                g = []
            else:
                raise(ValueError, 'unknown tag %r' % (tag,))

            for line in g:
                yield line

    def _my_plain_replace(self, a, alo, ahi, b, blo, bhi):
        assert alo < ahi and blo < bhi
        first  = self._dump('<', a, alo, ahi)
        second = self._dump('>', b, blo, bhi)

        for g in first, '---\n', second:
            for line in g:
                yield line


def pdiff(a, b):
    """
    Compare `a` and `b` (lists of strings); return a POSIX/Gnu "normal format" diff.
    """
    return POSIXDiffer().compare(a, b)


def compare_binary_files(file1, file2):
    # Compare sizes first.  Don't bother comparing unless sizes are the same.
    if os.path.getsize(file1) != os.path.getsize(file2):
        return False

    buffer_size = 8*1024
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            buffer1 = f1.read(buffer_size)
            buffer2 = f2.read(buffer_size)
            if buffer1 != buffer2:
                return False
            if not buffer1:
                return True

def compare_text_files(file1, file2):
    file1content = open(file1, 'U').readlines()
    file2content = open(file2, 'U').readlines()
    return pdiff(file1content, file2content)


def compare_directories(options, dir1, dir2):
    dc = filecmp.dircmp(dir1, dir2)

    incre = None
    if options.include:
        incre = re.compile(options.include)

    excre = None
    if options.exclude:
        excre = re.compile(options.exclude)

    # Apply inclusion/exclusion to "only in" files too.
    # Only print the header if there is at least one file that passes
    # the inclusion/exclusion.

    if dc.left_only:
        hdr = False
        for f in dc.left_only:
            passed = True

            if excre is not None and excre.search(f):
                passed = False

            if incre is not None and not incre.search(f):
                passed = False

            if passed:
                if not hdr:
                    print('Only in %s:' % (dc.left))
                    hdr = True
                print('    %s' % (f))

    if dc.right_only:
        hdr = False
        for f in dc.right_only:
            passed = True
            if excre is not None and excre.search(f):
                passed = False

            if incre is not None and not incre.search(f):
                passed = False

            if passed:
                if not hdr:
                    print('Only in %s:' % (dc.right))
                    hdr = True
                print('    %s' % (f))

    if dc.common_files:
        for common_file in dc.common_files:
            file1 = os.path.join(dc.left,  common_file)
            file2 = os.path.join(dc.right, common_file)

            # Skip this file if inclusion filter is in effect but
            # file does not match.
            if incre is not None and not incre.search(file1):
                continue

            # Skip this file if exclusion filter is in effect and
            # file matches.
            if excre is not None and excre.search(file1):
                continue

            title = 'diff %s %s' % (file1, file2)
            printed_title = False
            try:
                for difference in compare_text_files(file1, file2):
                    if options.brief:
                        # Found a difference.  Report it.  No need to continue.
                        print('%s %s : files are different' % (file1, file2))
                        break

                    # If we get to here, we are verbose (not brief).
                    # Print the title once...
                    if not printed_title:
                        print(title)
                        printed_title = True

                    # ...followed by the differences.
                    sys.stdout.writelines(difference)
            except UnicodeDecodeError:
                # Binary file.
                if options.binary and not compare_binary_files(file1, file2):
                    print('%s %s : binary files are different' % (file1, file2))

    # Descend down the tree into common directories.
    subre = None
    if options.subdir:
        subre = re.compile(options.subdir)
    for common_dir in dc.common_dirs:
        # Skip this subdirectory if subdirectory filter is in effect and
        # subdirectory matches.  Notice the fullmatch() here, not search().
        if subre is not None and subre.fullmatch(common_dir):
            continue

        compare_directories(
            options,
            os.path.join(dc.left,  common_dir),
            os.path.join(dc.right, common_dir))


def main(options):
    """
    This program is based on Python's difflib sample program, Tools/Scripts/diff.py.

    It produces differences in the POSIX format.

    See http://www.unix.com/man-page/POSIX/1posix/diff/
    """

    if not options.recursive:
        file1 = options.arg[0]
        if not os.path.isfile(file1):
            print('ERROR: %s is not a file' % (file1))
            return 1

        file2 = options.arg[1]
        if not os.path.isfile(file2):
            print('ERROR: %s is not a file' % (file2))
            return 1

        try:
            sys.stdout.writelines(compare_text_files(file1, file2))
        except UnicodeDecodeError:
            if options.binary and not compare_binary_files(file1, file2):
                print('%s %s : binary files are different' % (file1, file2))
    else:
        compare_directories(options, options.arg[0], options.arg[1])
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i',
        '--include',
        dest='include',
        help='Inclusion regex to apply to file path when performing recursive directory comparisons.')

    parser.add_argument(
        '-e',
        '--exclude',
        dest='exclude',
        help='Exclusion regex to apply to file path when performing recursive directory comparisons.')

    parser.add_argument(
        '-s',
        '--subdir',
        dest='subdir',
        help='Subdirectory exlusion regex to apply to subdirectory names when performing recursive directory comparisons.')

    parser.add_argument(
        '-b',
        '--binary',
        dest='binary',
        help='Compare and report on binary files.',
        action='store_true',
        default=False)

    parser.add_argument(
        '-r',
        '--recursive',
        dest='recursive',
        help='Recursively compare subdirectories.',
        action='store_true',
        default=False)

    parser.add_argument(
        '-q',
        '--brief',
        dest='brief',
        help='When performing recursive directory comparisons, only report when files are different.',
        action='store_true',
        default=False)

    parser.add_argument(
        'arg',
        help='Names of files or directories to compare.',
        nargs=2)

    options = parser.parse_args()

    sys.exit(main(options))

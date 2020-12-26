import os


def find_between(s: str, first: str, last: str):
    """Gives you the first thin between the two delimiters
    """
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end], end
    except ValueError:
        return "", 0


def iterate_over_folder(folder: str):
    for dirpath, _, files in os.walk(folder):
        for filename in files:
            yield os.path.join(dirpath, filename)

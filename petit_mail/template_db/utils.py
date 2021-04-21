import re
from typing import List
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
    """Walk into every folder and files
    """
    for dirpath, _, files in os.walk(folder):
        for filename in files:
            yield os.path.join(dirpath, filename)


def extract_variable(var: str):
    """Will attempt to get every variable inside the given strings
    """
    r = var.split('+')
    r = [
        i
        .replace('(', "")
        .replace(')', "")
        .strip()
        for i in r if '"' not in i
    ]
    return r


def get_placeholder(text: str, local_funcs: List[str]) -> List[str]:
    for name in local_funcs:
        text = text.replace(name, '')
    # finding between {{ }}
    res: List[str] = re.findall(
        r"\{{(.*?)\}}", text, re.MULTILINE
    )
    # res.extend(re.findall(
    #     r"{%(.*?)%}", text, re.MULTILINE
    # ))
    # finding between {% %}
    res2 = []
    for i in res:
        res2.extend(extract_variable(i.strip()))
    # extract variables
    return res2

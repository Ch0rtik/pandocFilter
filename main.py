import sys
from functools import reduce

from panflute import *

headers_map = {}


def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def upper_str(elem, doc):
    if isinstance(elem, Str):
        elem.text = elem.text.upper()


def action(elem: Header, doc):
    if isinstance(elem, Header):
        header_str = stringify(elem)

        if header_str in headers_map.keys():
            if elem.level in headers_map[header_str]:
                headers_map[header_str][elem.level] += 1
            else:
                headers_map[header_str][elem.level] = 1

        else:
            headers_map[header_str] = {}
            headers_map[header_str][elem.level] = 1

        if elem.level <= 3:
            elem.walk(upper_str)

    if isinstance(elem, Str):
        if elem.text.upper().startswith("BOLD") and elem.text.upper().count("BOLD") == 1:
            bold_index = elem.text.upper().find("BOLD")

            after_text = elem.text[bold_index + 4:]  # in case of "bold?", "bold?" is one Str. "?" is an aftertext.

            elem.parent.content.insert(elem.index + 1, Str(after_text))

            elem.text = elem.text[bold_index:bold_index + 4]
            return Strong(elem)


def join_levels(levels):
    return ",\n  ".join(str(times) + (" times" if times > 1 else " time ")
                        + " in level " + str(level) for level, times in levels.items())


def main(doc=None):
    result = run_filter(action, doc=doc)
    for header, levels in headers_map.items():
        if sum(levels.values()) > 1:
            errprint('"' + header + '"', "header repeats:\n ", join_levels(levels))

    return result


if __name__ == '__main__':
    main()

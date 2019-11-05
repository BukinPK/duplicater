import re
from pprint import pprint
from tqdm import tqdm


def make_data(text, sep='\r?\n\s*[-—]+\s*\r?\n'):
    return [re.split(r'[\r\n]+', p.strip()) for p in re.split(sep, text)]

def get_matches(data, len_for_match=2):
    res = {}
    for n, p in enumerate(tqdm(data)):
        match = {}
        for sn, s in enumerate(p):

            for n2, p2 in enumerate(data[n+1:], n+1):
                for sn2, s2 in enumerate(p2):

                    if check(s, s2):
                        if not match.get(n2):
                            match[n2] = {sn: sn2}
                        else:
                            match[n2].update({sn: sn2})
        match = {k: v for k, v in match.items() if len(v) >= len_for_match}
        if match:
            res.update({n: match})
    return res

def check(s1, s2):
    s1 = re.sub(r'\W', '', s1.lower())
    s2 = re.sub(r'\W', '', s2.lower())
    return s1 and s2 and s1 == s2

def print_all(data, match, deleted=[]):
    for k, v in match.items():
        temp = []
        if k in deleted:
            continue
        root_str = set(k for val in v.values() for k in val.keys())
        temp.append(f'\n\n{k}{"-"*40}\n\n\n' + f'\n'.join([
            ('>> ' if sn in root_str else '   ')
            + s for sn, s in enumerate(data[k])]))

        for k2, v2 in v.items():
            if k2 in deleted:
                continue
            temp.append(f'{k2}{"-"*30}\n' + '\n'.join([
                ('>> ' if sn2 in v2.values() else '   ')
                + s2 for sn2, s2 in enumerate(data[k2])]))

        if len(temp) > 1:
            print(f'\n'.join(temp))


if __name__ == '__main__':
    data = make_data(open('test_data.txt').read())
    matches = get_matches(data)
    print_all(data, matches)

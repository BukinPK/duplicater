import re
from tg_tqdm import tg_tqdm


def make_data(text, sep='\r?\n\s*[-—]+\s*\r?\n'):
    return [re.split(r'\r?\n', p.strip()) for p in re.split(sep, text)]

def get_matches(data, TOKEN, user_id, message_id, desc='', len_for_match=2):
    res = {}
    for n, p in enumerate(tg_tqdm(data, TOKEN, user_id, message_id, desc=desc,
                          bar_format='{desc}{bar}|{percentage:3.0f}%',
                          show_last_update=False)):
        match = {}
        for sn, s in enumerate(p):

            for n2, p2 in enumerate(data[n+1:], n+1):
                for sn2, s2 in enumerate(p2):

                    if check(s, s2):
                        if not match.get(n2):
                            match[n2] = {str(sn): sn2}
                        else:
                            match[n2].update({str(sn): sn2})
        match = {str(k): v for k, v in match.items() if len(v) >= len_for_match}
        if match:
            res.update({str(n): match})
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

def get_one(data, matches, deleted=[], passed=[]):
    items = [(int(k), v) for k, v in matches.items()]
    for k, v in items:
        if k in passed:
            continue
        post_numbers = []
        temp = []
        if k not in deleted:
            root_str = set(int(k) for v2 in v.values() for k in v2.keys())
            temp.append(f'\n'.join([
                ('>> ' if sn in root_str else '   ')
                + s for sn, s in enumerate(data[k])]))
            post_numbers.append(k)

        matched_items = [(int(k), v) for k, v in v.items()]
        for k2, v2 in matched_items:
            if k2 in deleted or k2 in passed:
                continue
            temp.append(f'{"-"*40}\n' + '\n'.join([
                ('>> ' if sn2 in v2.values() else '   ')
                + s2 for sn2, s2 in enumerate(data[k2])]))
            post_numbers.append(k2)

        if len(temp) > 1:
            return post_numbers, f'\n'.join(temp)
    return [], 'all done'

def get_final(data: list, deleted: list):
    data = ['\n'.join(text) for n, text in enumerate(data) if n not in deleted]
    return '\n\n<hr />\n\n'.join(data)

if __name__ == '__main__':
    data = make_data(open('test_data.txt').read())
    matches = get_matches(data)
    print_all(data, matches)

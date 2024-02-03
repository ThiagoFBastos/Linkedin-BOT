import json
from unidecode import unidecode

def normalize(s):
    s = unidecode(s).lower()
    return ' '.join([w for w in s.split() if not w.isspace()])

def write_variants():
    with open('keywords.json', 'r') as fp:
        keywords = json.load(fp)

    key_id = dict([(normalize(key), pos + 1) for pos, key in enumerate(keywords.keys())])
    insertions = []

    for key, words in keywords.items():
        key = normalize(key)
        for word in words:
            word = normalize(word)
            insertions.append(f"INSERT INTO variants (name, keyword_id) VALUES ('{word}', {key_id[key]});")

    return '\n'.join(insertions)

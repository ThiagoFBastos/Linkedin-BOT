import json
from unidecode import unidecode

def normalize(s):
    s = unidecode(s).lower()
    return ' '.join([w for w in s.split() if not w.isspace()])

def write_keywords():
    with open('keywords.json', 'r') as fp:
        keywords = json.load(fp)

    insertions = []

    for key in keywords.keys():
        key = normalize(key)
        insertions.append(f"INSERT INTO keywords (name) VALUES ('{key}');")

    return '\n'.join(insertions)

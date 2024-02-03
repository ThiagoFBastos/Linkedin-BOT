import json
from unidecode import unidecode

def normalize(s):
    s = unidecode(s).lower()
    return ' '.join([w for w in s.split() if not w.isspace()])

def write_dependencies():
    with open('keywords.json') as fp:
        keywords = json.load(fp)

    with open('correlations.json') as fp:
        dependencies = json.load(fp)

    key_id = dict([(normalize(key), pos + 1) for pos, key in enumerate(keywords.keys())])
    insertions = []

    for child, parents in dependencies.items():
        child = normalize(child)
        child_id = key_id[child]
        for parent in parents:
            parent = normalize(parent)
            parent_id = key_id[parent]
            insertions.append(f"INSERT INTO dependencies (parent_keyword_id, child_keyword_id) VALUES ({parent_id}, {child_id});")

    return '\n'.join(insertions)

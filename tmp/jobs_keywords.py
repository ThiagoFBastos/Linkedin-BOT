import json
from unidecode import unidecode

def normalize(s):
    s = unidecode(s).lower()
    return ' '.join([w for w in s.split() if not w.isspace()])

def write_jobs_keywords():
    with open('keywords.json', 'r') as fp:
        keywords = json.load(fp)

    with open('posts.json', 'r') as fp:
        posts = json.load(fp)
        posts = posts['data']

    key_id = dict([(normalize(key), pos + 1) for pos, key in enumerate(keywords.keys())])
    which_key = dict()

    for key, words in keywords.items():
        key = normalize(key)
        for word in words:
            word = normalize(word)
            which_key[word] = key_id[key]

    insertions = []

    for post_id, post in enumerate(posts):
        post_id += 1
        
        for word in post['keywords']:
            word = normalize(word)
            word_key_id = which_key[word]
            insertions.append(f"INSERT INTO jobs_keywords (job_id, key_id) VALUES ({post_id}, {word_key_id});")

    return '\n'.join(insertions)
    

import json
from unidecode import unidecode

def normalize(s):
    s = unidecode(s).lower()
    return ' '.join([w for w in s.split() if not w.isspace()])

def write_jobs():

    with open('posts.json', 'r') as fp:
        posts = json.load(fp)
        posts = posts['data']

    insertions = []

    for post in posts:
        title = normalize(post['title'])
        weight = post['weight']
        insertions.append(f"INSERT INTO jobs (title, weight) VALUES ('{title}', {weight});")

    return '\n'.join(insertions)


    

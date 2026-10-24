import json, re, collections
db = json.load(open('all.json'))
secs = {s['s']: s for s in db}
index = {}
for s in db:
    for it in s['items']:
        index.setdefault(re.sub(r'\s+',' ',it['q']).strip().lower(), []).append(it)
def norm(q): return re.sub(r'\s+',' ',q).strip().lower()

added = collections.Counter(); tagged = 0; focus = 0
def add(sec, q, a, dup, isfocus=False):
    global tagged, focus
    k = norm(q)
    if dup.strip():
        hits = index.get(norm(dup))
        if hits:
            for it in hits:
                if 'poh' not in it['doc'].split():
                    it['doc'] += ' poh'; tagged += 1
                if isfocus: it['focus'] = 1
            return
    if k in index:
        for it in index[k]:
            if 'poh' not in it['doc'].split(): it['doc'] += ' poh'; tagged += 1
        return
    it = {'q': q, 'a': a, 'doc': 'poh'}
    if isfocus: it['focus'] = 1; focus += 1
    secs[sec]['items'].append(it)
    index[k] = [it]
    added[sec] += 1

for e in json.load(open('gsp/out-warrior.json')):
    add(e['s'], e['q'], e['a'], e.get('dup',''), e.get('focus', False))

wb = json.load(open('wb-worked.json'))
for e in wb['questions']:
    add('Performance and Limitations', e['q'], e['a'], e.get('dup',''), False)

json.dump(db, open('all.json','w'), ensure_ascii=False, indent=1)
print('tagged existing with poh:', tagged)
print('new added:', dict(added), 'total new', sum(added.values()), 'focus', focus)
print('TOTAL items:', sum(len(s['items']) for s in db))
print(collections.Counter(i['doc'] for s in db for i in s['items']))

import json, re, collections

db = json.load(open('all.json'))

# 1. migrate doc -> space-separated token set
MAP = {'chs':'chs', 'fi':'fi', 'both':'chs fi', 'acs':'acs'}
index = {}            # normalized question -> item
for s in db:
    for it in s['items']:
        it['doc'] = MAP[it['doc']]
        index.setdefault(re.sub(r'\s+',' ',it['q']).strip().lower(), []).append(it)

def norm(q): return re.sub(r'\s+',' ',q).strip().lower()

secs = {s['s']: s for s in db}

added = collections.Counter()
tagged = 0
unmatched = []
new_items = collections.defaultdict(list)

for f in ['out01','out06','out11','out16','out21','out27']:
    for e in json.load(open('gsp/%s.json' % f)):
        dup = (e.get('dup') or '').strip()
        if dup:
            hits = index.get(norm(dup))
            if hits:
                for it in hits:
                    if 'gs' not in it['doc'].split():
                        it['doc'] += ' gs'
                        tagged += 1
                continue
            unmatched.append((f, e['page'], dup[:80]))
            # fall through: treat as new
        new_items[e['s']].append({'q': e['q'], 'a': e['a'], 'doc': 'gs',
                                  'page': e['page'], 'concept': e.get('concept','')})
        added[e['s']] += 1

# de-dupe new items against each other (same question text from two pages)
seen = {}
for sec, lst in new_items.items():
    keep = []
    for it in lst:
        k = norm(it['q'])
        if k in seen or k in index:
            if k in index:
                for ex in index[k]:
                    if 'gs' not in ex['doc'].split():
                        ex['doc'] += ' gs'
            continue
        seen[k] = it
        keep.append(it)
    new_items[sec] = keep

for sec, lst in new_items.items():
    secs[sec]['items'].extend(lst)

json.dump(db, open('all.json','w'), ensure_ascii=False, indent=1)

print('tagged existing with gs:', tagged)
print('unmatched dup strings:', len(unmatched))
for u in unmatched[:15]: print('   ', u)
print('new items added per section:')
for s,n in sorted(added.items(), key=lambda x:-x[1]): print('   %-32s %d -> kept %d' % (s, n, len(new_items[s])))
print('TOTAL items now:', sum(len(s['items']) for s in db))
print('doc tally:', collections.Counter(i['doc'] for s in db for i in s['items']))

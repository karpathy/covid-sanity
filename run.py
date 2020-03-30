"""
Run to update all the database json files that can be served from the website
"""

import json
import requests
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import stop_words
from sklearn import svm

# -----------------------------------------------------------------------------

jstr = requests.get('https://connect.biorxiv.org/relate/collection_json.php?grp=181')
jall = jstr.json()
print("writing jall.json")
json.dump(jall, open('jall.json', 'w'))

# compute tfidf features with scikit learn
print("fitting tfidf")
max_features = 2000
v = TfidfVectorizer(input='content',
        encoding='utf-8', decode_error='replace', strip_accents='unicode',
        lowercase=True, analyzer='word', stop_words='english',
        token_pattern=r'(?u)\b[a-zA-Z_][a-zA-Z0-9_-]+\b',
        ngram_range=(1, 1), max_features = max_features,
        norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=True,
        max_df=1.0, min_df=1)
corpus = [a['rel_abs'] for a in jall['rels']]
v.fit(corpus)

# use tfidf features to find nearest neighbors cheaply
X = v.transform(corpus)
D = np.dot(X, X.T).todense()
IX = np.argsort(-D, axis=1)
sim = {}
ntake = 40
n = IX.shape[0]
for i in range(n):
    ixc = [int(IX[i,j]) for j in range(ntake)]
    ds = [int(D[i,IX[i,j]]*1000) for j in range(ntake)]
    sim[i] = list(zip(ixc, ds))
print("writing sim.json")
json.dump(sim, open('sim.json', 'w'))

# use exemplar SVM to build similarity instead
print("fitting SVMs per paper")
svm_sim = {}
ntake = 40
for i in range(n):
    # everything is 0 except the current index - i.e. "exemplar svm"
    y = np.zeros(X.shape[0])
    y[i] = 1
    clf = svm.LinearSVC(class_weight='balanced', verbose=False, max_iter=10000, tol=1e-4, C=1.0)
    clf.fit(X,y)
    s = clf.decision_function(X)
    IX = np.argsort(-s)
    ixc = [int(IX[j]) for j in range(ntake)]
    ds = [int(D[i,IX[j]]*1000) for j in range(ntake)]
    svm_sim[i] = list(zip(ixc, ds))
json.dump(svm_sim, open('svm_sim.json', 'w'))

# construct a reverse index for suppoorting search
vocab = v.vocabulary_
idf = v.idf_
english_stop_words = stop_words.ENGLISH_STOP_WORDS
punc = "'!\"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'" # removed hyphen from string.punctuation
trans_table = {ord(c): None for c in punc}

def makedict(s, forceidf=None, scale=1.0):
    words = set(s.lower().translate(trans_table).strip().split())
    words = set(w for w in words if len(w) > 1 and (not w in english_stop_words))
    idfd = {}
    for w in words: # todo: if we're using bigrams in vocab then this won't search over them
        if forceidf is None:
            if w in vocab:
                idfval = idf[vocab[w]] * scale # we have idf for this
            else:
                idfval = 1.0 * scale # assume idf 1.0 (low)
        else:
            idfval = forceidf
        idfd[w] = idfval
    return idfd

def merge_dicts(dlist):
    m = {}
    for d in dlist:
        for k,v in d.items():
            m[k] = m.get(k,0) + v
    return m

search_dict = []
for p in jall['rels']:
    dict_title = makedict(p['rel_title'], forceidf=10, scale=3)
    dict_authors = makedict(p['rel_authors'], forceidf=5)
    dict_summary = makedict(p['rel_abs'])
    qdict = merge_dicts([dict_title, dict_authors, dict_summary])
    search_dict.append(qdict)

print("writing search.json")
json.dump(search_dict, open('search.json', 'w'))

"""
Run to update all the database json files that can be served from the website
"""

from tqdm import tqdm
import json
import requests
import numpy as np

# -----------------------------------------------------------------------------

def write_json(obj, filename, msg=''):
    suffix = f'; {msg}' if msg else ''
    print(f"writing {filename}{suffix}")
    with open(filename, 'w') as f:
        json.dump(obj, f)


def calculate_tfidf_features(rels, max_features=5000, max_df=1.0, min_df=3):
    """ compute tfidf features with scikit learn """
    from sklearn.feature_extraction.text import TfidfVectorizer
    v = TfidfVectorizer(input='content',
                        encoding='utf-8', decode_error='replace', strip_accents='unicode',
                        lowercase=True, analyzer='word', stop_words='english',
                        token_pattern=r'(?u)\b[a-zA-Z_][a-zA-Z0-9_-]+\b',
                        ngram_range=(1, 1), max_features=max_features,
                        norm='l2', use_idf=True, smooth_idf=True, sublinear_tf=True,
                        max_df=max_df, min_df=min_df)
    corpus = [(a['rel_title'] + '. ' + a['rel_abs']) for a in rels]
    X = v.fit_transform(corpus)
    X = np.asarray(X.astype(np.float32).todense())
    print("tfidf calculated array of shape ", X.shape)
    return X, v


def calculate_sim_dot_product(X, ntake=40):
    """ take X (N,D) features and for each index return closest ntake indices via dot product """
    S = np.dot(X, X.T)
    IX = np.argsort(S, axis=1)[:, :-ntake-1:-1] # take last ntake sorted backwards
    return IX.tolist()


def calculate_sim_svm(X, ntake=40):
    """ take X (N,D) features and for each index return closest ntake indices using exemplar SVM """
    from sklearn import svm
    n, d = X.shape
    IX = np.zeros((n, ntake), dtype=np.int64)
    print(f"training {n} svms for each paper...")
    for i in tqdm(range(n)):
        # set all examples as negative except this one
        y = np.zeros(X.shape[0], dtype=np.float32)
        y[i] = 1
        # train an SVM
        clf = svm.LinearSVC(class_weight='balanced', verbose=False, max_iter=10000, tol=1e-4, C=0.1)
        clf.fit(X, y)
        s = clf.decision_function(X)
        ix = np.argsort(s)[:-ntake-1:-1] # take last ntake sorted backwards
        IX[i] = ix
    return IX.tolist()


def build_search_index(rels, v):
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

    # construct a reverse index for suppoorting search
    vocab = v.vocabulary_
    idf = v.idf_
    punc = "'!\"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'" # removed hyphen from string.punctuation
    trans_table = {ord(c): None for c in punc}

    def makedict(s, forceidf=None):
        words = set(s.lower().translate(trans_table).strip().split())
        words = set(w for w in words if len(w) > 1 and (not w in ENGLISH_STOP_WORDS))
        idfd = {}
        for w in words: # todo: if we're using bigrams in vocab then this won't search over them
            if forceidf is None:
                if w in vocab:
                    idfval = idf[vocab[w]] # we have a computed idf for this
                else:
                    idfval = 1.0 # some word we don't know; assume idf 1.0 (low)
            else:
                idfval = forceidf
            idfd[w] = idfval
        return idfd

    def merge_dicts(dlist):
        m = {}
        for d in dlist:
            for k, v in d.items():
                m[k] = m.get(k,0) + v
        return m

    search_dict = []
    for p in rels:
        dict_title = makedict(p['rel_title'], forceidf=10)
        rel_authors_str = ' '.join(a['author_name'] + ' ' + a['author_inst'] for a in p['rel_authors'])
        dict_authors = makedict(rel_authors_str, forceidf=5)
        dict_summary = makedict(p['rel_abs'])
        qdict = merge_dicts([dict_title, dict_authors, dict_summary])
        search_dict.append(qdict)

    return search_dict


if __name__ == '__main__':

    # fetch the raw data from biorxiv
    jstr = requests.get('https://connect.biorxiv.org/relate/collection_json.php?grp=181')
    jall = jstr.json()
    write_json(jall, 'jall.json', f"{len(jall['rels'])} papers")

    # calculate feature vectors for all abstracts and keep track of most similar other papers
    X, v = calculate_tfidf_features(jall['rels'])
    sim_svm = calculate_sim_svm(X)
    write_json(sim_svm, 'sim_tfidf_svm.json')

    # calculate the search index to support search
    search_dict = build_search_index(jall['rels'], v)
    write_json(search_dict, 'search.json')

"""
Simple flask server for the interface
"""

import json
import argparse

from flask import Flask, request, redirect, url_for
from flask import render_template
# -----------------------------------------------------------------------------

app = Flask(__name__)

# load raw paper data
with open('jall.json', 'r') as f:
    jall = json.load(f)

# load computed paper similarities
with open('svm_sim.json', 'r') as f:
    sim_dict = json.load(f)

# load search dictionary for each paper
with open('search.json', 'r') as f:
    search_dict = json.load(f)

# do some precomputation since we're going to be doing lookups of doi -> doc index
doi_to_ix = {}
for i, j in enumerate(jall['rels']):
    doi_to_ix[j['rel_doi']] = i

# -----------------------------------------------------------------------------
# routes below

@app.route("/search", methods=['GET'])
def search():
    q = request.args.get('q', '') # get the search request
    if not q:
        return redirect(url_for('main')) # if someone just hits enter with empty field

    qparts = q.lower().strip().split() # split by spaces

    # accumulate scores
    n = len(jall['rels'])
    scores = []
    for i, sd in enumerate(search_dict):
        score = sum(sd.get(q, 0) for q in qparts)
        if score == 0:
            continue # no match whatsoever, dont include
        score += 1.0 * (n - i)/n # give a small boost to more recent papers (low index)
        scores.append((score, jall['rels'][i]))
    scores.sort(reverse=True, key=lambda x: x[0]) # descending
    papers = [x[1] for x in scores if x[0] > 0]
    if len(papers) > 40:
        papers = papers[:40]
    gvars = {'sort_order': 'search', 'search_query': q, 'num_papers': len(jall['rels'])}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

@app.route('/sim/<doi_prefix>/<doi_suffix>')
def sim(doi_prefix=None, doi_suffix=None):
    doi = f"{doi_prefix}/{doi_suffix}" # reconstruct the full doi
    pix = doi_to_ix.get(doi)
    if pix is None:
        papers = []
    else:
        sim_ix, match = zip(*sim_dict[str(pix)][:40]) # indices of closest papers
        papers = [jall['rels'][cix] for cix in sim_ix]
    gvars = {'sort_order': 'sim', 'num_papers': len(jall['rels'])}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

@app.route('/')
def main():
    papers = jall['rels'][:40]
    gvars = {'sort_order': 'latest', 'num_papers': len(jall['rels'])}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

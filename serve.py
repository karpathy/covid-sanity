"""
Simple flask server for the interface
"""

import json
import argparse

from flask import Flask, request
from flask import render_template
# -----------------------------------------------------------------------------

app = Flask(__name__)

@app.route("/search", methods=['GET'])
def search():
    q = request.args.get('q', '') # get the search request
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
    if len(papers) > args.num_results:
        papers = papers[:args.num_results]
    gvars = {'sort_order': 'search', 'search_query': q}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

@app.route('/sim/<doi_prefix>/<doi_suffix>')
def sim(doi_prefix=None, doi_suffix=None):
    doi = f"{doi_prefix}/{doi_suffix}" # reconstruct the full doi
    pix = doi_to_ix.get(doi)
    if pix is None:
        papers = []
    else:
        sim_ix, match = zip(*sim[str(pix)][:args.num_results]) # indices of closest papers
        papers = [jall['rels'][cix] for cix in sim_ix]
    gvars = {'sort_order': 'sim'}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

@app.route('/')
def main():
    papers = jall['rels'][:args.num_results]
    gvars = {'sort_order': 'latest'}
    context = {'papers': papers, 'gvars': gvars}
    return render_template('index.html', **context)

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # process input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prod', dest='prod', action='store_true', help='run in prod?')
    parser.add_argument('-n', '--num_results', type=int, default=40, help='number of results per query')
    parser.add_argument('--port', dest='port', type=int, default=5000, help='port to serve on')
    parser.add_argument('--https', dest='https', type=int, default=0, help='use https?')
    args = parser.parse_args()
    print(args)

    # load raw paper data
    with open('jall.json', 'r') as f:
        jall = json.load(f)

    # load computed paper similarities
    with open('sim.json', 'r') as f:
        sim = json.load(f)

    # load search dictionary for each paper
    with open('search.json', 'r') as f:
        search_dict = json.load(f)

    # do some precomputation since we're going to be doing lookups of doi -> doc index
    doi_to_ix = {}
    for i, j in enumerate(jall['rels']):
        doi_to_ix[j['rel_doi']] = i

    if args.prod:
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop
        from tornado.log import enable_pretty_logging
        enable_pretty_logging()
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(args.port)
        IOLoop.instance().start()
    else:
        print('starting flask!')
        app.debug = False
        app.run(port=args.port, host='0.0.0.0')

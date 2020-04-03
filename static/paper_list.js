'use strict';

const Paper = props => {
  const p = props.paper
  const url = p.rel_link + '.full.pdf';
  return (
    <div class={'rel_paper ' + p.rel_site}>
      <div class='dllinks'>
        <div class='metadata action'><a href={'/sim/' + p.rel_doi}>show similar</a></div>
        <div class='metadata action'><a href={url}>pdf</a></div>
        <div class='metadata rel_date'>{p.rel_date}</div>
      </div>
      <div class='rel_title'><a href={p.rel_link}>{p.rel_title}</a></div>
      <div class='rel_authors'>{p.rel_authors}</div>
      <div class='rel_abs'>{p.rel_abs}</div>
    </div>
  )
}

const PaperList = props => {
  const lst = props.papers;
  const plst = lst.map((jpaper, ix) => <Paper key={ix} paper={jpaper} />);
  const msg = {
    "latest": "Showing latest papers:",
    "sim": 'Showing papers most similar to the first one:',
    "search": 'Search results for "' + gvars.search_query + '":'
  }
  return (
    <div>
      <div id="info">{msg[gvars.sort_order]}</div>
      <div id="paperList" class="rel_papers">
        {plst}
      </div>
    </div>
  )
}

ReactDOM.render(<PaperList papers={papers}/>, document.getElementById('wrap'));

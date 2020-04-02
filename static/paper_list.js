'use strict';

class Paper extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const p = this.props.paper;
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
    );
  }
}

class PaperList extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {

    // render all papers
    const lst = this.props.papers;
    const plst = lst.map((jpaper, ix) => {
      return (
        <Paper paper={jpaper} />
      )
    });

    // combine into a wrapper div
    var msg = '';
    if(gvars.sort_order === 'latest') {
      msg = 'Showing latest papers:';
    } else if(gvars.sort_order === 'sim') {
      msg = 'Showing papers most similar to the first one:';
    } else if(gvars.sort_order === 'search') {
      msg = 'Search results for "' + gvars.search_query + '":';
    }
    return (
      <div>
        <div id="info">{msg}</div>
        <div id="paperList" class="rel_papers">
          {plst}
        </div>
      </div>
    )

  }
}

ReactDOM.render(<PaperList papers={papers}/>, document.getElementById('wrap'));

'use strict';

const Tweet = props => {
  const t = props.tweet;
  const turl = "https://twitter.com/" + t.name + "/status/" + t.id;
  return (
    <div class='tweet'>
      <a href={turl}><img src={t.image_url}></img></a>
      <div class='meta'>
        <span class="following">{t.followers}</span>
        <span class="uname"><a href={turl}>{t.name}</a></span>
        <span class="text">{t.text}</span>
      </div>
    </div>
  )
}

class Tweets extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      collapsed: true,
      max_items: 10,
    };
  }

  render() {
    const tlist = this.props.tweets;
    if(tlist.length === 0) {
      // return an empty element if no tweets are present
      return (null);
    } else {
      if(this.state.collapsed) {
        // show just summary statistic of the tweets
        return (
          <div class='rel_tweets_summary' onClick={() => this.setState({collapsed: false})}>{tlist.length} tweets</div>
        )
      } else {
        // show tweets in expanded view
        const tlist_comps = tlist.map((jtweet, ix) => <Tweet key={ix} tweet={jtweet} />);
        return (
          <div class='rel_tweets'>{tlist_comps}</div>
        );
      }
    }
  }
}

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
      <Tweets tweets={p.tweets} />
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


# covid-sanity

This small flask app organizes bioarxiv papers about COVID-19 and makes them searchable, sortable, etc.

It is running live on [biomed-sanity.com](http://biomed-sanity.com/). I could not register covid-sanity.com because the term is "protected".

Effectively a search interface on top of the [bioarxiv page](https://connect.biorxiv.org/relate/content/181)

Follows my previous project in spirit, [arxiv-sanity](https://github.com/karpathy/arxiv-sanity-preserver)

License: MIT

## run

As this is a flask app running it locally is straight forward. First compute the database with `run.py` and then serve:

```
$ python run.py
$ flask run
```

To deploy in production I recommend NGINX and Gunicorn. After configuring NGINX in your environment something like

```
$ gunicorn3 --workers=3 serve:app --access-logfile -
```

will do the trick.




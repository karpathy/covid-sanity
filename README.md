
# covid-sanity

This project organizes COVID-19 SARS-CoV-2 preprints from medRxiv and bioRxiv. The raw data comes from the [bioRxiv](https://connect.biorxiv.org/relate/content/181) page, but this project makes the data searchable, sortable, etc. The "most similar" search uses an exemplar SVM trained on tfidf feature vectors from the abstracts of these papers. The project is running live on [biomed-sanity.com](http://biomed-sanity.com/). (I could not register covid-sanity.com because the term is "protected")

![user interface](https://raw.github.com/karpathy/covid-sanity/master/ui.png)

Since I can't assess the quality of the similarity search I welcome any opinions on some of the hyperparameters. For instance, the parameter `C` in the SVM training and the size of the feature vector `max_features` (currently set at 2,000) dramatically impact the results.

This project follows a previous one of mine in spirit, [arxiv-sanity](https://github.com/karpathy/arxiv-sanity-preserver).

## run

As this is a flask app running it locally is straight forward. First compute the database with `run.py` and then serve:

```
$ pip install -r requirements.txt
$ python run.py
$ export FLASK_APP=serve.py
$ flask run
```

To deploy in production I recommend NGINX and Gunicorn. [Linode](https://www.linode.com/) is one easy/cheap way to host the application on the internet and they have [detailed tutorials](https://www.linode.com/docs/development/python/flask-and-gunicorn-on-ubuntu/) one can follow.

## License

MIT

Introduction
===============

In recent years, Knowledge Graph Embedding (KGE) methods have been applied in benchmark
datasets including Wikidata_, Freebase_, DBpedia_,
and YAGO_. Applications of KGE methods include fact prediction, question answering, and recommender systems.

KGE is an active area of research and many authors have provided reference software implementations.
However, most of these are standalone reference implementations and therefore it is difficult and
time-consuming to:

(i) find the source code
(ii) adapt the source code to new datasets
(iii) correctly parameterize the models
(iv) compare against other methods

Recently, this problem has been partially addressed by libraries such as OpenKE_ and AmpliGraph_ that provide a
framework common to several KGE methods. However, these frameworks take different perspectives, make specific
assumptions, and thus the resulting implementations diverge substantially from the original architectures.
Furthermore, these libraries often force the user to use preset hyperparameters, or make implicit use of
golden hyperparameters, and thus make it tedious and time-consuming to adapt the models to new datasets.

**To solve these issues we propose pykg2vec which is a single Python library with large collection of state-of-the-art
KGE methods. The goals of pykg2vec are to be practical and educational.** The practical value is achieved through:

(a) proper use of GPUs and CPUs
(b) a set of tools to automate the discovery of golden hyperparameters
(c) a set of visualization tools for the training and results of the embeddings

The educational value is achieved through:

(d) a modular and flexible software architecture and KGE pipeline
(e) access to a large number of state-of-the-art KGE models

.. _Wikidata: https://cacm.acm.org/magazines/2014/10/178785-wikidata/fulltext
.. _Freebase: http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.538.7139&rep=rep1&type=pdf
.. _DBpedia: https://cis.upenn.edu/~zives/research/dbpedia.pdf
.. _YAGO: https://www2007.org/papers/paper391.pdf
.. _OpenKE: https://github.com/thunlp/OpenKE
.. _AmpliGraph: https://github.com/Accenture/AmpliGraph
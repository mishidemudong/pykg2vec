#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import tensorflow as tf
sys.path.append("../")

from core.KGMeta import ModelMeta
from utils.visualization import Visualization

class SMELinear(ModelMeta):
    """
    ------------------Paper Title-----------------------------
    A Semantic Matching Energy Function for Learning with Multi-relational Data
    ------------------Paper Authors---------------------------
    Antoine Bordes
    Universite de Technologie de Compiegne – CNRS
    Heudiasyc UMR 7253
    Compiegne, France
    antoine.bordes@utc.fr
    Jason Weston
    Google
    111 8th avenue
    New York, NY, USA
    jweston@google.com
    Xaiver Glorot, Joshua Bengio
    Universite de Montreal
    Monteal, QC, Canada
    {glorotxa, bengioy}@iro.umontreal.ca
    ------------------Summary---------------------------------
    Semantic Matching Energy (SME) is an algorithm for embedding multi-relational data into vector spaces. 
    SME conducts semantic matching using neural network architectures. Given a fact (h, r, t), it first projects 
    entities and relations to their embeddings in the input layer. Later the relation r is combined with both h and t
    to get gu(h, r) and gv(r, t) in its hidden layer. The score is determined by calculating the matching score of gu and gv.

    There are two versions of SME: a linear version(SMELinear) as well as bilinear(SMEBilinear) version which differ in how the hidden layer is defined.

    Portion of Code Based on https://github.com/glorotxa/SME/blob/master/model.py
    """
    def __init__(self, config=None, data_handler=None):
        self.config = config
        self.data_handler = data_handler
        self.model_name = 'SMELinear'
        
    def def_inputs(self):
        with tf.name_scope("read_inputs"):
            self.pos_h = tf.placeholder(tf.int32, [None])
            self.pos_t = tf.placeholder(tf.int32, [None])
            self.pos_r = tf.placeholder(tf.int32, [None])
            self.neg_h = tf.placeholder(tf.int32, [None])
            self.neg_t = tf.placeholder(tf.int32, [None])
            self.neg_r = tf.placeholder(tf.int32, [None])
            self.test_h = tf.placeholder(tf.int32, [1])
            self.test_t = tf.placeholder(tf.int32, [1])
            self.test_r = tf.placeholder(tf.int32, [1])

    def def_parameters(self):
        num_total_ent = self.data_handler.tot_entity
        num_total_rel = self.data_handler.tot_relation
        k = self.config.hidden_size

        with tf.name_scope("embedding"):
            self.ent_embeddings = tf.get_variable(name="ent_embedding",
                                                  shape=[num_total_ent, k],
                                                  initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.rel_embeddings = tf.get_variable(name="rel_embedding",
                                                  shape=[num_total_rel, k],
                                                  initializer=tf.contrib.layers.xavier_initializer(uniform=False))
        with tf.name_scope("weights_and_parameters"):

            self.mu1 = tf.get_variable(name="mu1", shape=[k, k],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.mu2 = tf.get_variable(name="mu2", shape=[k, k],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.bu  = tf.get_variable(name="bu",  shape=[k, 1],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.mv1 = tf.get_variable(name="mv1", shape=[k, k],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.mv2 = tf.get_variable(name="mv2", shape=[k, k],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            self.bv  = tf.get_variable(name="bv",  shape=[k, 1],
                                       initializer=tf.contrib.layers.xavier_initializer(uniform=False))

        self.parameter_list = [self.ent_embeddings, self.rel_embeddings, \
                               self.mu1, self.mu2, self.bu, \
                               self.mv1, self.mv2, self.bv]
    def def_loss(self):

        with tf.name_scope('normalization'):
            self.ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
            self.rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, axis=1)
        
        with tf.name_scope('lookup_embeddings'):
            pos_h_e = tf.nn.embedding_lookup(self.ent_embeddings, self.pos_h)
            pos_r_e = tf.nn.embedding_lookup(self.rel_embeddings, self.pos_r)
            pos_t_e = tf.nn.embedding_lookup(self.ent_embeddings, self.pos_t)
            neg_h_e = tf.nn.embedding_lookup(self.ent_embeddings, self.neg_h)
            neg_r_e = tf.nn.embedding_lookup(self.rel_embeddings, self.neg_r)
            neg_t_e = tf.nn.embedding_lookup(self.ent_embeddings, self.neg_t)

        energy_pos_l = self.gu(pos_h_e, pos_r_e) 
        energy_pos_r = self.gv(pos_r_e, pos_t_e)
        energy_pos   = tf.reduce_sum(tf.multiply(energy_pos_l, energy_pos_r), 1)

        energy_neg_l = self.gu(neg_h_e, neg_r_e) 
        energy_neg_r = self.gv(neg_r_e, neg_t_e)
        energy_neg   = tf.reduce_sum(tf.multiply(energy_neg_l, energy_neg_r), 1)

        self.loss = tf.reduce_sum(tf.maximum(energy_neg + self.config.margin - energy_pos, 0))

    def gu(self, h, r):
        return tf.transpose(tf.matmul(self.mu1, tf.transpose(h)) + tf.matmul(self.mu2, tf.transpose(r)) + self.bu)

    def gv(self, r, t):
        return tf.transpose(tf.matmul(self.mv1, tf.transpose(r)) + tf.matmul(self.mv2, tf.transpose(t)) + self.bv)

    def test_step(self):
        num_entity = self.data_handler.tot_entity

        with tf.name_scope('lookup_embeddings'):
            h_vec = tf.nn.embedding_lookup(self.ent_embeddings, self.test_h)
            r_vec = tf.nn.embedding_lookup(self.rel_embeddings, self.test_r)
            t_vec = tf.nn.embedding_lookup(self.ent_embeddings, self.test_t)
 
        energy_h_l = self.gu(self.ent_embeddings, r_vec)
        energy_h_r = self.gv(r_vec, t_vec)
        energy_h   = tf.multiply(energy_h_l, energy_h_r)

        energy_t_l = self.gu(h_vec, r_vec)
        energy_t_r = self.gv(r_vec, self.ent_embeddings)
        energy_t   = tf.multiply(energy_t_l, energy_t_r)

        with tf.name_scope('normalization'):
            self.ent_embeddings = tf.nn.l2_normalize(self.ent_embeddings, axis=1)
            self.rel_embeddings = tf.nn.l2_normalize(self.rel_embeddings, axis=1)

        with tf.name_scope('lookup_embeddings'):
            norm_h_vec = tf.nn.embedding_lookup(self.ent_embeddings, self.test_h)
            norm_r_vec = tf.nn.embedding_lookup(self.rel_embeddings, self.test_r)
            norm_t_vec = tf.nn.embedding_lookup(self.ent_embeddings, self.test_t)

        norm_energy_h_l = self.gu(self.ent_embeddings, norm_r_vec)
        norm_energy_h_r = self.gv(norm_r_vec, norm_t_vec)
        norm_energy_h   = tf.multiply(norm_energy_h_l, norm_energy_h_r)

        norm_energy_t_l = self.gu(norm_h_vec, norm_r_vec)
        norm_energy_t_r = self.gv(norm_r_vec, self.ent_embeddings)
        norm_energy_t   = tf.multiply(norm_energy_t_l, norm_energy_t_r)

        _, self.head_rank      = tf.nn.top_k(tf.reduce_sum(tf.negative(energy_h), 1), k=num_entity)
        _, self.tail_rank      = tf.nn.top_k(tf.reduce_sum(tf.negative(energy_t), 1), k=num_entity)
        _, self.norm_head_rank = tf.nn.top_k(tf.reduce_sum(tf.negative(norm_energy_h), 1), k=num_entity)
        _, self.norm_tail_rank = tf.nn.top_k(tf.reduce_sum(tf.negative(norm_energy_t), 1), k=num_entity)

        return self.head_rank, self.tail_rank, self.norm_head_rank, self.norm_tail_rank

    def embed(self, h, r, t):
        """function to get the embedding value"""
        emb_h = tf.nn.embedding_lookup(self.ent_embeddings, h)
        emb_r = tf.nn.embedding_lookup(self.rel_embeddings, r)
        emb_t = tf.nn.embedding_lookup(self.ent_embeddings, t)
        return emb_h, emb_r, emb_t

    def predict_embed(self, h, r, t, sess=None):
        """function to get the embedding value in numpy"""
        if not sess:
            raise NotImplementedError('No session found for predicting embedding!')
        emb_h, emb_r, emb_t = self.embed(h, r, t)
        h, r, t = sess.run([emb_h, emb_r, emb_t])
        return h, r, t   

    def summary(self):
        """function to print the summary"""
        print("\n----------------SUMMARY----------------")
        # Acquire the max length and add four more spaces
        maxspace = len(max([k for k in self.config.__dict__.keys()])) + 15
        for key, val in self.config.__dict__.items():
            if 'gpu' in key:
                continue
            if len(key) < maxspace:
                for i in range(maxspace - len(key)):
                    key = ' ' + key
            print(key, ":", val)
        print("-----------------------------------------")

    def display(self, sess=None):
        """function to display embedding"""
        if self.config.plot_embedding:
            triples = self.data_handler.validation_triples_ids[:self.config.disp_triple_num]
            viz = Visualization(triples=triples,
                                idx2entity=self.data_handler.idx2entity,
                                idx2relation=self.data_handler.idx2relation)

            viz.get_idx_n_emb(model=self, sess=sess)
            viz.reduce_dim()
            viz.plot_embedding(resultpath=self.config.figures, algos=self.model_name)

        if self.config.plot_training_result:
            viz = Visualization()
            viz.plot_train_result(path=self.config.result,
                                  result=self.config.figures,
                                  algo=['TransE', 'TransR', 'TransH'],
                                  data=['Freebase15k'])

        if self.config.plot_testing_result:
            viz = Visualization()
            viz.plot_test_result(path=self.config.result,
                                 result=self.config.figures,
                                 algo=['TransE', 'TransR', 'TransH'],
                                 data=['Freebase15k'], paramlist=None, hits=self.config.hits)
#!/usr/bin/env python

from abc import abstractmethod, ABCMeta
import numpy as np
import ghmm as gh


class CreateHMMAbstractclass():
    """Abstract class for HMM generation"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.num_possible_states = None # This has to be set by the specific imprelementation

    def get(self, **kwargs):
        # TODO: Some error checking

        # If no errors, create HMM
        return self.create(**kwargs)

    def get_num_possible_states(self):
        return self.num_possible_states

    def _create_sequence_set(self, qsr_seq, symbols):
        """Creating a sequence set for training

        :param qsr_seq: the observation seqence of symbols according to the alphabet as a list of lists
        :param symbols: the alphabet of possible symbols

        :return: the sequence set for the given observations
        """
        return gh.SequenceSet(symbols, qsr_seq)

    def create_transition_matrix(self, size, **kwargs):
        """Method for the creation of the transition probability matrix. Creates
        a uniformly distributed matrix. Please override if special behaviour
        is necessary.

        :return: uniform SIZExSIZE transition matrix as a numpy array
        """

        trans = np.ones([size,size])
        return trans/trans.sum(axis=1)

    def create_emission_matrix(self, size, **kwargs):
        """Method for the creation of the emission probability matrix. Creates
        a uniformly distributed matrix. Please override if special behaviour
        is necessary.

        :return: uniform SIZExSIZE emission matrix as a numpy array
        """

        emi = np.ones([size,size])
        return emi/emi.sum(axis=1)

    @abstractmethod
    def qsr_to_state(self, qsr_data):
        """Transforms a list of qsr state chains to a list of lists of numbers according to the alphabet.
        Needs to be overridden by the specific QSR to handle the correct symbols.

        :return: List of lists containing the qsr input data as symbols from the alphabet
            E.g.: [[1,4,2,7],[0,5,3,8,5,1,3]]
        """
        return

    def _generate_alphabet(self, num_symbols):
        """Generate a simple integer alphabet: [0:num_symbols-1]"""
        return gh.IntegerRange(0, num_symbols)

    def _train(self, seq, trans, emi, num_possible_states):
        """Uses the given parameters to train a multinominal HMM to represent
        the given seqences of observations. Uses Baum-Welch training.
        Please override if special training is necessary for your QSR.

        :param seq: the sequence of observations represented by alphabet symbols
        :param trans: the transition matrix as a numpy array
        :param emi: the emission matrix as a numpy array
        :param num_possible_states: the total number of possible states

        :return: the via baum-welch training generated hmm
        """

        print 'Generating HMM:'
        print '\tCreating symbols...'
        symbols = self._generate_alphabet(num_possible_states)
        startprob = np.zeros(num_possible_states)
        startprob[0] = 1
        print '\t\t', symbols
        print '\tCreating HMM...'
        hmm = gh.HMMFromMatrices(
            symbols,
            gh.DiscreteDistribution(symbols),
            trans.tolist(),
            emi.tolist(),
            startprob.tolist()
        )
        print '\tTraining...'
        hmm.baumWelch(self._create_sequence_set(seq, symbols))

        return hmm


    def create(self, **kwargs):
        """Creates and trains (using '_train') a HMM to represent the given qtc sequences.
        Main function to create and train the hmm. Please override with special
        behaviour is necessary.

        This function is called by the library to create the hmm.

        :param **kwargs:
            - qsr_seq: the sequence of QSRs. This should be a list of state
        chains, i.e. a list of lists

        :return: The trained HMM

        """

        state_seq = self.qsr_to_state(kwargs["qsr_seq"])
        trans = self.create_transition_matrix(size=self.get_num_possible_states(), **kwargs)
        emi = self.create_emission_matrix(size=self.get_num_possible_states(), **kwargs)
        hmm = self._train(state_seq, trans, emi, self.get_num_possible_states())
        print '...done'
        return hmm

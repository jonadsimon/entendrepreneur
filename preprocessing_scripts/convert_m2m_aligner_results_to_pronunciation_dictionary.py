import numpy as np
from nltk.corpus import cmudict
import sys
sys.path.insert(0, '../code') # need to add the code path for other imports to work
from word import Word
from sequence_alignment import SequenceAlignment
from pronunciation_dictionary import PronunciationDictionary

# Aligned pairs use the following syntax:
# 1) chunked graphemes/phonemes are divided by '|' symbols
# 2) two graphemes/phonemes which are chunked together in a mapping will be separated by a ':'
# 3) graphemes mapping to null-phonemes are denoted by '_'
DIVIDER_CHAR = '|'
CONCAT_CHAR = ':'
NULL_CHAR = '_' # null char can also appear in the grapheme sequence, but NOT as a null-graph

# CMU Pronouncing Dictionary
cmu_dict = cmudict.dict()

def m2m_grapheme_to_grapheme_chunks(m2m_grapheme):
    '''
    Convert from an m2m-aligned grapheme represention to a tuple-based grapheme represention
    e.g. 'i|m|p|e|l:l|e|d|' --> [('i',),('m',),('p',),('e',),('l','l',),('e',),('d',)]
    '''
    grapheme_chunks = m2m_grapheme.strip(DIVIDER_CHAR).split(DIVIDER_CHAR)
    new_grapheme_chunks = []
    for chunk in grapheme_chunks:
        # do NOT filter out null_chars
        new_chunk = tuple(chunk.split(CONCAT_CHAR))
        new_grapheme_chunks.append(new_chunk)
    return new_grapheme_chunks

def m2m_phoneme_to_phoneme_chunks(m2m_phoneme):
    '''
    Convert from an m2m-aligned phoneme represention to a tuple-based phoneme represention
    e.g. 'IH|M|P|EH|L|_|D|' --> [('IH',),('M',),('P',),('EH',),('L',),('_',),('D',)]
    '''
    phoneme_chunks = m2m_phoneme.strip(DIVIDER_CHAR).split(DIVIDER_CHAR)
    new_phoneme_chunks = []
    for chunk in phoneme_chunks:
        # DO filter out null_chars, here denoting silent-letters
        if chunk == NULL_CHAR:
            new_chunk = ()
        else:
            new_chunk = tuple(chunk.split(CONCAT_CHAR))
        new_phoneme_chunks.append(new_chunk)
    return new_phoneme_chunks

def grapheme_chunks_to_grapheme_string(grapheme_chunks):
    '''
    Convert from a tuple-based grapheme represention to a string-based grapheme represention
    e.g. [('i',),('m',),('p',),('e',),('l','l',),('e',),('d',)] --> 'impelled'
    '''
    return ''.join(sum(map(list, grapheme_chunks), []))

def phoneme_chunks_to_stressed_phoneme_chunks(phoneme_chunks, grapheme):
    '''
    Convert from stressless phonememe represention to a stressed phoneme represention
    e.g. [('IH',),('M',),('P',),('EH',),('L',),('_',),('D',)] --> [('IH0',),('M',),('P',),('EH1',),('L',),('_',),('D',)]
    '''
    chunk_lengths = map(len, phoneme_chunks)
    valid_end_inds = np.cumsum(chunk_lengths)
    valid_start_inds = np.cumsum(chunk_lengths) - chunk_lengths
    idx_pairs = zip(valid_start_inds,valid_end_inds)

    stressed_phoneme = cmu_dict[grapheme][0]
    stressed_phoneme_chunks = [tuple(stressed_phoneme[start_idx:end_idx]) for (start_idx,end_idx) in idx_pairs]
    return stressed_phoneme_chunks, stressed_phoneme

# Load the aligned grapheme/phoneme pairs
with open('../data/g2p_alignment/m2m_preprocessed_cmudict.txt.m-mAlign.2-2.delX.1-best.conYX.align') as infile:
    aligned_grapheme_phoneme_pairs = [line.strip().split('\t') for line in infile.readlines()]

# Use the aligned grapheme/phoneme pairs to create a PronunciationDictionary
word_list = []
for m2m_grapheme, m2m_phoneme in aligned_grapheme_phoneme_pairs:
    grapheme_chunks = m2m_grapheme_to_grapheme_chunks(m2m_grapheme)
    grapheme = grapheme_chunks_to_grapheme_string(grapheme_chunks)

    phoneme_chunks = m2m_phoneme_to_phoneme_chunks(m2m_phoneme)
    stressed_phoneme_chunks, stressed_phoneme = phoneme_chunks_to_stressed_phoneme_chunks(phoneme_chunks, grapheme)

    grapheme_phoneme_aligment = SequenceAlignment(grapheme_chunks, stressed_phoneme_chunks)

    new_word = Word(grapheme, stressed_phoneme, grapheme_phoneme_aligment)
    word_list.append(new_word)

# Save the PronunciationDictionary
PronunciationDictionary(word_list).save('../data/pronunciation_dictionary.pkl')

import array
import difflib
import logging
import random

import nltk
import numpy
import numpy as np
from flask import abort
# from gensim.models import Word2Vec
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet

from app.constants.DATAPROCESSING_CONSTANTS import delete_actions, combine_actions, actions_list, ignorance_words, \
    sum_actions


# ******************* nltk.pos_tag **************
# CC	Coordinating conjunction	and
# CD	Cardinal number	one, two
# DT	Determiner	the, a
# EX	Existential there	there
# FW	Foreign word	dolce
# IN	Preposition or subordinating conjunction	of, in, by
# JJ	Adjective	big
# JJR	Adjective, comparative	bigger
# JJS	Adjective or superlative	biggest
# LS	List item marker	1)
# MD	Modal	could, will
# NN	Noun, singular or mass	turnip, badger
# NNS	Noun, plural	turnips, badgers
# NNP	Proper noun, singular	Edinburgh
# NNPS	Proper noun, plural	Smiths
# PDT	Predeterminer	all, both
# POS	Possessive ending	's
# PRP	Personal pronoun	I, you, he
# PRP$	Possessive pronoun	my, your, his
# RB	Adverb	quickly
# RBR	Adverb, comparative	more quickly
# RBS	Adverb, superlative	most quickly
# RP	Particle	up, off
# TO	Infinite marker	to
# UH	Interjection	oh, oops
# VB	Verb, base form	take
# VBD	Verb, past tense	took
# VBG	Verb, gerund or present participle	taking
# VBN	Verb, past participle	taken
# VBP	Verb, non-3rd person singular present	take
# VBZ	Verb, 3rd person singular present	takes
# WDT	Wh-determiner	which, that, what
# WP	Wh-pronoun	what, who
# WP$	Possessive wh-pronoun	whose
# WRB	Wh-adverb	how, where, when
# ***************** end nltk.pos_tag ************

class WordProcessor:


    # def _train_altrnatives_model(self, sentences=default_sentences):
    #
    #     # Train the Word2Vec model
    #     model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)
    #
    #     # Save the trained model
    #     model.save("word2vec.model")

    # def get_alternative_words(self, word):
    #     try:
    #         # Load the pre-trained Word2Vec model
    #         model = Word2Vec.load("word2vec.model")
    #
    #         # Get the most similar words to the entered word
    #         alternatives = model.wv.most_similar(word)
    #
    #         # Print the alternative words
    #         if len(alternatives) > 0:
    #             for alternative in alternatives:
    #                 print(alternative)
    #     except Exception as e:
    #         print("There is no any alternatives")

    def generate_alternative_sentences(self, sentence):
        words = sentence.split()
        alternative_sentences = []
        for i in range(len(words)):
            alternative_word = random.choice(sentence)
            if alternative_word != words[i]:
                alternative_sentence = sentence.replace(words[i], alternative_word)
                alternative_sentences.append(alternative_sentence)
        return alternative_sentences

    def get_closest_words(self, compare_list, words: array):

        closet_words = []

        for i in range(len(words)):
            # Get the closest spelling match from the word list
            closest_match = difflib.get_close_matches(words[i], compare_list, n=1, cutoff=0.6)

            # Print the closest spelling match
            if len(closest_match) != 0 and closest_match[0] not in closet_words:
                closet_words.append(closest_match[0])
                return closet_words

        return closet_words

    def extract_keywords(self, user_desc):
        try:
            # Analysing the input
            text_names = [token for token, pos in pos_tag(word_tokenize(user_desc)) if pos.startswith('N')]
            text_names = numpy.array(text_names)

            text_verbs = [token for token, pos in pos_tag(word_tokenize(user_desc)) if
                          (pos.startswith('VB') or pos.startswith('VBG') or pos.startswith('VBN') or pos.startswith(
                              'VBP') or pos.startswith('VBZ'))]
            text_verbs = numpy.array(text_verbs)

            text_numbers = [token for token, pos in pos_tag(word_tokenize(user_desc)) if (pos.startswith('CD'))]
            text_numbers = numpy.array(text_numbers)

            if len(text_names) == 0 or len(text_verbs) == 0:
                return "Sorry but we couldn't recognise what you need, Please rephrase your description and try again"

            return text_verbs, text_names

        except  Exception as e:
            logging.ERROR('Ohh -get_model_status...Something went wrong.')
            return ['Ohh -get_model_status...Something went wrong.']

    def find_synonyms(self, words):
        all_synonyms = {}
        for word in words:
            synonyms = []
            for syn in wordnet.synsets(word):
                for i in syn.lemmas():
                    synonyms.append(i.name())
            synonyms = numpy.array(synonyms)
            all_synonyms[word] = synonyms
        return all_synonyms

    def find_antonyms(self, words):
        all_antonyms = {}
        for word in words:
            antonyms = []
            for syn in wordnet.synsets(word):
                for i in syn.lemmas():
                    if i.antonyms():
                        antonyms.append(i.antonyms()[0].name())
            antonyms = numpy.array(antonyms)
            all_antonyms[word] = antonyms
        return all_antonyms

    def get_actions(self, user_text):

        actions, attributes = self.extract_keywords(user_text)
        actions_synonyms = self.find_synonyms(actions)
        attributes_synonyms = self.find_synonyms(attributes)

        for synonyms in actions_synonyms:
            word_synonyms = actions_synonyms[synonyms]
            print("{}:".format(word_synonyms))

        return 0

    def get_changes_list(self, user_text):
        try:
            actions_flow = {}
            # 1- Get keywords
            text_verbs, text_names = self.extract_keywords(user_text)

            # 2- Extract all synonyms
            # Extract actions
            synonyms_verbs = self.find_synonyms(text_verbs)
            target_verbs = [k for k in synonyms_verbs if k not in ignorance_words]
            for synonyms_verb in synonyms_verbs:
                all_synonyms = synonyms_verbs[synonyms_verb]
                act_list = self.get_closest_words(actions_list, all_synonyms)
                if len(act_list) > 0:
                    target_verbs.append(act_list)

            target_verbs = numpy.array(target_verbs).flatten()

            # Extract column names
            synonyms_names = text_names
            target_names = [k for k in synonyms_names if k not in ignorance_words]
            target_names = numpy.array(target_names).flatten()

            if len(target_verbs) == 1:
                actions_flow[target_verbs[0]] = target_names[0]

            return actions_flow

        except Exception as e:
            abort(500, description=e)

    def _get_orders_list(self, sentence):
        # Tokenize the sentence into words
        words = nltk.word_tokenize(sentence)

        # Use NLTK to tag each word with its part of speech
        pos_tags = nltk.pos_tag(words)

        # Create a list to store verbs and their corresponding words
        verb_list = []

        # Loop through each word and its POS tag
        for i in range(len(pos_tags)):
            word = pos_tags[i][0]
            pos = pos_tags[i][1]

            # Check if the word is a verb
            if pos.startswith('VB'):
                # Find all the words that come with this verb
                verb_words = [word]

                # Look at the next few words and their POS tags
                for j in range(i + 1, len(pos_tags)):
                    next_word = pos_tags[j][0]
                    next_pos = pos_tags[j][1]

                    # If the next word is a noun or adjective, add it to the verb_words list
                    if next_pos.startswith('NN') or next_pos.startswith('JJ'):
                        verb_words.append(next_word)
                    else:
                        break

                # Add the verb and its corresponding words to the verb_list
                verb_list.append((word, verb_words))

        # Print the list of verbs and their corresponding words
        print(verb_list)

    def get_orders_list(self, sentence, columns_list):
        # Define the action keywords
        columns_list = np.array(columns_list)

        # Tokenize the sentence into words
        words = nltk.word_tokenize(sentence)

        # Use NLTK to tag each word with its part of speech
        pos_tags = nltk.pos_tag(words)

        # Create a list to store the required actions
        required_actions = []

        # Loop through each word and its POS tag
        for i in range(len(pos_tags)):
            word = pos_tags[i][0]
            pos = pos_tags[i][1]

            # Check if the word is an action keyword
            if word.lower() in delete_actions or word.lower() in combine_actions or word.lower() in sum_actions:
                # Find all the objects that need to be acted upon
                object_words = []

                # Look at the next few words and their POS tags
                for j in range(i + 1, len(pos_tags)):
                    next_word = pos_tags[j][0]
                    next_pos = pos_tags[j][1]

                    # If the next word is a noun, add it to the object_words list
                    if next_pos.startswith('NN'):
                        action_item = True if next_word.lower() in columns_list else False
                        if action_item:
                            object_words.append(next_word)
                    elif next_pos.startswith('VB'):
                        break
                    else:
                        continue

                # Add the action and its corresponding objects to the required_actions list
                if word.lower() in delete_actions:
                    word = "Delete"
                elif word.lower() in sum_actions:
                    word = "Sum"
                else:
                    word = "Merge"

                required_actions.append((word, object_words))

        sorted_required_actions = sorted(required_actions, key=lambda x: x[0], reverse=True)

        return sorted_required_actions

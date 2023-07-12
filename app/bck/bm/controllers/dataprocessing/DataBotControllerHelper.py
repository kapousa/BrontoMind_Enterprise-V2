import logging

import openai
import spacy
from flask import abort
from sklearn.metrics.pairwise import cosine_similarity

from app.modules.base.constants.DATAPROCESSING_CONSTANTS import delete_action, merge_action, sum_action
from app.modules.base.constants.k import F, S, T


class DataBotControllerHelper:
    # Define alternative words
    delete_words = ['delete', 'remove', 'drop',
                    'erase',
                    'eliminate',
                    'omit',
                    'exclude',
                    'discard',
                    'cut',
                    'expunge',
                    'purge',
                    'clear',
                    'wipe out',
                    'strip']

    sum_words = ['sum', 'total',
                 'aggregate',
                 'add up',
                 'add',
                 'tally',
                 'count',
                 'calculate',
                 'accumulate',
                 'compute',
                 'summate',
                 'tabulate',
                 'agglomerate',
                 'amass',
                 'combine',
                 'consolidate',
                 'aggregize']

    merge_words = ['combine',
                   'unify',
                   'join',
                   'consolidate',
                   'integrate',
                   'blend',
                   'fuse',
                   'incorporate',
                   'synthesize',
                   'converge',
                   'meld',
                   'amalgamate',
                   'cohere',
                   'homogenize',
                   'incorporate']

    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.members = ['Tiger', 'Elephant', 'Wild Cat']

    def apply_bot_changes(self, required_changes, data):
        """
        Extract required changes from the input of the bot and apply them on the given data.
        @param required_changes:
        @param data:
        @return: modified data
        """
        try:
            df = data
            for change in required_changes:
                if change[0] == sum_action:
                    merged_col_name = 'Total of ' + ', '.join(change[1]).lower()
                    merged_columns = [x.lower() for x in change[1]]
                    df[merged_col_name] = 0
                    # Iterate over the columns and sum their values
                    for column in merged_columns:
                        df[merged_col_name] += df[column]
                if change[0] == merge_action:
                    merged_col_name = '_'.join(change[1]).lower()
                    merged_columns = [x.lower() for x in change[1]]
                    df[merged_columns] = df[merged_columns].astype(str)
                    df[merged_col_name] = df[merged_columns].apply("-".join, axis=1)
                    df = df.drop(merged_columns, axis="columns")
                if change[0] == delete_action:
                    for item in change[1]:
                        df = df.drop(item.lower(), axis="columns")
            return df
        except Exception as e:
            logging.exception(e)
            abort(500, description=e)

    def update_csv_with_text(self, df, text):
        try:
            # Process the text using OpenAI
            oak = "{0}{1}{2}".format(F, S, T)
            openai.api_key = oak

            # Define the conversation with the user
            conversation = [
                {'role': 'user', 'content': text}
            ]

            # Send the messages to the model
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation,
                max_tokens=100
            )

            # Extract the required actions from the model's response
            actions = []
            required_actions =[]
            for res in response:
                if res == 'choices':
                    message = response['choices'][0]
                    if message['message']['role'] == 'assistant' and message['message']['content'] != '':
                        actions.append(message['message']['content'])

            # Process the actions
            for action in actions:
                matching_columns = []
                if 'delete' in action:
                    # Perform delete action
                    column_name = action.split('delete')[1]  # Extract the column name to delete
                    if column_name in df.columns:
                        matching_columns.append(column_name)
                        df.drop(column_name, axis=1, inplace=True)

                if 'add' in action:
                    # Perform add action
                    column_name = action.split('add')[1]  # Extract the new column name
                    source_column = action.split('add_')[3]  # Extract the source column
                    if source_column in df.columns:
                        matching_columns.append(column_name)
                        df[column_name] = df[source_column].apply(lambda x: x / 2)  # Replace with the desired logic

                required_actions.append((action, matching_columns))

            return required_actions, df

        except Exception as e:
            logging.exception(e)
            abort(500, description=e)


    def find_closest_word(self, target_word, text):
        '''
        Find the closest word in given text
        @param target_word:
        @param text:
        @return: closest word of target word
        '''
        nlp = spacy.load("en_core_web_md")  # Load spaCy model with word vectors

        # Tokenize the text
        doc = nlp(text)

        closest_word = None
        max_similarity = 0.0  # Threshold for considering a close match

        # Iterate through each word in the text
        for token in doc:
            similarity = cosine_similarity(
                nlp(target_word).vector.reshape(1, -1),
                token.vector.reshape(1, -1)
            )[0][0]

            if similarity > max_similarity:
                closest_word = token.text
                max_similarity = similarity

        return closest_word

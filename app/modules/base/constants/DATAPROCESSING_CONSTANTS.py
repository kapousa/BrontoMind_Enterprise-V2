default_sentences = [["this", "is", "a", "sentence"],
                     ["this", "is", "another", "sentence"],
                     ["yet", "another", "sentence"],
                     ["one", "more", "sentence"],
                     ["and", "the", "final", "sentence"]]

combine_actions = [
    'amalgamate',
    'associate',
    'blend',
    'coalesce',
    'cohere',
    'combine',
    'compound',
    'connect',
    'consolidate',
    'converge',
    'fuse',
    'harmonize',
    'homogenize',
    'incorporate'
    'incorporate',
    'integrate',
    'join',
    'link',
    'meld',
    'merge',
    'mingle',
    'mix',
    'synthesize',
    'unify',
    'unite',
]

delete_actions = [
    'clear',
    'cut',
    'delete',
    'discard',
    'eliminate',
    'erase',
    'exclude',
    'expunge',
    'omit',
    'purge',
    'strip'
    'wipe out',
    'blot out',
    'cancel',
    'clear',
    'detach',
    'drop',
    'eliminate',
    'eradicate',
    'excise',
    'expunge',
    'extract',
    'obliterate',
    'remove',
    'scrub',
    'wipe out'
]

sum_actions = ['sum', 'total',
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

ignorance_words = ['column', 'columns', 'row', 'rows', 'and', 'or', 'the', 'a', 'an', '.', ',', '?', '!']

training_date = ['The two companies decided to combine their resources to increase efficiency.',
                 'The departments decided to merge their operations to improve customer service.',
                 'The groups worked to unite their efforts to achieve a common goal.',
                 'The individuals chose to join forces to make a difference in their community.',
                 'The ingredients were blended together to create a unique flavor.',
                 'The colors were mixed to form a new shade.',
                 'The two pieces were fused together to form a single entity.',
                 'The scattered ideas were coalesced into a comprehensive plan.',
                 'The companies aimed to consolidate their power through a merger.',
                 'The systems were integrated to improve overall performance.',
                 'The cultures were made to mingle in a melting pot of diversity.',
                 'The opposing ideas were harmonized into a single vision.',
                 'The organizations associated themselves with a shared mission.',
                 'The concepts were linked to form a coherent understanding.',
                 'The separate entities connected to form a network of support.',
                 'The components were compounded to form a more complex structure.',
                 'The elements were synthesized to form a new substance.']

actions_list = ['merge', 'delete']

delete_action = 'Delete'

merge_action = 'Merge'

sum_action = 'Sum'

modified_files_temp_path = 'tempfiles/'

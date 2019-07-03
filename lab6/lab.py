# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences

import os.path

TEST_DIRECTORY = os.path.dirname(__file__)

class Trie:

    def __init__(self):
        self.value = None
        self.children = dict()
        self.type = None

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        # check and set type
        if self.type is not None:
            if not isinstance(key, self.type):
                raise TypeError
        else: 
            self.type = type(key)

        # base case
        if len(key) == 0:
            self.value = value
            return

        # type can be either str or tuple 
        if self.type is str:
            char = key[0]
        if self.type is tuple:
            char = (key[0],)

        # recursively set item
        if char in self.children.keys():
            return self.children[char].__setitem__(key[1:], value)
        else:
            next_t = Trie()
            self.children.update({char:next_t})
            return next_t.__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        # check exceptions 
        if key is None:
            raise KeyError
        if not isinstance(key, self.type):
            raise TypeError

        # base case
        if len(key) == 0:
            if self.value is not None:
                return self.value    
            else:
                raise KeyError

        # type can be either str or tuple   
        if self.type is str:
            char = key[0]
        if self.type is tuple:
            char = (key[0],) 

        # recursively search 
        if char in self.children.keys():
            return self.children[char].__getitem__(key[1:])
        else:
            raise KeyError

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists.
        """
        return self.__setitem__(key, None)

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        try:
            temp = self.__getitem__(key)
            return True
        except:
            return False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        if self.type is str:
            init = ''
        else:
            init = ()
        # words: maps each trie to the str or tuple that leads to this trie from the root self.
        words = {self: init}
        return self.traverse(words)

    def traverse(self, words):
        """
        Helper function for __iter__
        """
        if self is not None:
            for char, trie in self.children.items():
                prefix = words[self]
                word = prefix + char
                words.update({trie: word})
                for pair in trie.traverse(words):
                    yield pair
            if self.value is not None: # if self is the end of a word
                yield (words[self], self.value)

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    t = Trie()
    values = dict()
    sentences = tokenize_sentences(text)

    # count the frequency for each word
    for sentence in sentences:
        word_list = sentence.split()
        for word in word_list:
            if word not in values:
                values.update({word: 0})
            values[word] += 1

    # update the trie
    for key in values.keys():
        t[key] = values[key]
    return t


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    t = Trie()
    values = dict()
    sentences = tokenize_sentences(text)

    # count the frequency for each sentence
    for sentence in sentences:
        word_tuple = tuple(sentence.split())
        if word_tuple not in values:
            values.update({word_tuple: 0})
        values[word_tuple] += 1

    # update the trie
    for key in values.keys():
        t[key] = values[key]
    return t

def find_end_of_prefix(trie, prefix):
    """
    Return the last trie when we search for prefix from trie
    """
    # base case
    if len(prefix) == 0:
        return trie

    # type can be either str or tuple 
    if trie.type is tuple:
        char = (prefix[0],)
    else:
        char = prefix[0]

    # recursively search
    for c in trie.children.keys():
        if c == char:
            return find_end_of_prefix(trie.children[c], prefix[1:])
    return Trie()


def autocomplete(trie, prefix, max_count=None, as_tuple=False):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    if not isinstance(prefix, trie.type):
        raise TypeError

    last_trie = find_end_of_prefix(trie, prefix)
    if last_trie.type is None or max_count == 0:
        return []

    # suggested is the list of words from trie sorted by values
    suggested = list(last_trie)
    if suggested is None:
        return []
    suggested.sort(key=lambda pair: pair[1], reverse = True)

    result = []
    if max_count is not None:
        size = min(len(suggested), max_count)
    else:
        size = len(suggested)

    if not as_tuple:
        # cutoff the list
        for i in range(size):
            result.append(prefix + suggested[i][0])
    else:
        for i in range(size):
            result.append((prefix+suggested[i][0], suggested[i][1]))
    return result

def check_edit(words, prefix, complete):
    """
    Check all possible strings in the list words that are one edit away from prefix, excluding
    strings in the list complete

    Parameters:
        words (list): list of words to consider
        prefix (str): find strings that are similar to prefix
        complete (list): do not consider strings already in complete

    Return:
        result (list): the list of strings one edit away from prefix
    """
    result = []
    for word, value in words: 
        if word not in complete:
            d = len(word) - len(prefix)

            if d in[-1,0,1]:
                w = min(1+d,1)
                p = min(1-d,1)
                for i in range(len(word)+1):
                    if word[:i]==prefix[:i] and word[i+w:]==prefix[i+p:]:
                        result.append((word,value))
                        break  
                if d == 0:
                    for i in range(len(word)-1):
                        if word[i]==prefix[i+1] and word[i+1]==prefix[i]:
                            if word[:i]==prefix[:i] and word[i+2:]==prefix[i+2:]:                            
                                result.append((word,value))
                                break
    return result

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    complete = autocomplete(trie, prefix, max_count)
    if max_count is not None and max_count <= len(complete):
        return complete

    all_words = list(trie)
    single_edits = check_edit(all_words, prefix,complete)

    # append single edits to the list
    if max_count is None:
        n = len(single_edits)
    else:
        n = max_count - len(complete)
    single_edits.sort(key=lambda pair: pair[1], reverse = True)
    for i in range(n):
        complete.append(single_edits[i][0])

    return complete

def simplify_star(pattern):
    """
    Remove consecutive * from pattern
    """
    new_pattern = pattern[0]
    for i in range(1,len(pattern)):
        if pattern[i]== '*' and pattern[i-1]=='*':
            continue
        new_pattern += pattern[i]
    return new_pattern

def recurse_filter(trie, pattern, word = '', answers = set()):
    """
    Recursively find words that match the pattern

    Parameters:
        trie (Trie): where we start the search
        pattern (str): the pattern that we try to match
        word (str): the string that leads to trie from the root
        answers (set): the set of words that match the pattern so far
    """
    # if trie is the end of a word
    if trie.value is not None:
        if len(pattern) == 0 or pattern == '*':
            answers.add((word, trie.value))

    # base case
    if len(pattern) == 0:
        return answers

    # check if we skip *
    if pattern[0] == '*': 
        skip_star = recurse_filter(trie, pattern[1:], word, answers)
        if skip_star is not None:
            answers |= skip_star

    for char, next_trie in trie.children.items():
        new_word = word + char

        if pattern[0] == '*': 
            new_ans = recurse_filter(next_trie, pattern, new_word, answers) 
            if new_ans is not None:         
                answers |= new_ans

        elif pattern[0] == char or pattern[0] == '?':
            new_ans = recurse_filter(next_trie, pattern[1:], new_word, answers)
            if new_ans is not None:
                answers |= new_ans

    return answers

def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    pattern = simplify_star(pattern)
    return list(recurse_filter(trie, pattern, '', set()))

# you can include test cases of your own in the block below.
if __name__ == '__main__':
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'pp.txt'), encoding='utf-8') as f:
        pp = f.read()
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'alice.txt'), encoding='utf-8') as f:
        alice = f.read()
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'dracula.txt'), encoding='utf-8') as f:
        dracula = f.read()
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'attc.txt'), encoding='utf-8') as f:
        attc = f.read()
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'meta.txt'), encoding='utf-8') as f:
        meta = f.read()

    alice_sentence = make_phrase_trie(alice)
    print(autocomplete(alice_sentence, (), 6),'\n')

    meta_word = make_word_trie(meta)
    print(autocomplete(meta_word, 'gre', 6),'\n')

    print(word_filter(meta_word, 'c*h'), '\n')

    attc_word = make_word_trie(attc)
    print(word_filter(attc_word, 'r?c*t'),'\n')

    alice_word = make_word_trie(alice)
    print(autocorrect(alice_word, 'hear', 12),'\n')

    pp_word = make_word_trie(pp)
    print(autocorrect(pp_word, 'hear'),'\n')

    dracula_word = make_word_trie(dracula)
    print(len(list(dracula_word)),'\n')

    total_words = 0
    for word, freq in list(dracula_word):
        total_words += freq
    print(total_words,'\n')

    print(len(list(alice_sentence)),'\n')

    total_sentences = 0
    for sentence, freq in list(alice_sentence):
        total_sentences += freq
    print(total_sentences,'\n')   

    pass

# coding=utf-8

"""
Original code from:
https://towardsdatascience.com/markov-chains-how-to-train-text-generation-to-write-like-george-r-r-martin-cdc42786e4b6
"""

from scipy.sparse import dok_matrix
from random import randint


'''
How to write Parameters.txt
------------------------------------------------------------------------------------------------------------------------
DirectoryName
"FileName0"< "FileName2">< "FileName2"><...>
k (= length of phrases from text to train with, e.g. k = 2 with "a b c d" would use phrases "a b", "b c", and "c d")
seed (a phrase to begin generation; it should be part of the training text and have k words)
chain_length (= length of the final generated text in number of words)
------------------------------------------------------------------------------------------------------------------------

These values are used to fill the list parameters[] and are used in the program as described.
Note characters in the list ['.', '-', ',', '!', '?', '(', '—', ')'] will be counted as separate words!
Certain characters like \\n and \\t are ignored completely, and do not include them in the parameter.

'''


# https://stackoverflow.com/questions/30069846/how-to-find-out-chinese-or-japanese-character-in-a-string-in-python
CJK_RANGES = [
  {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},          # compatibility ideographs
  {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},          # compatibility ideographs
  {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},          # compatibility ideographs
  {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")},  # compatibility ideographs
  {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},          # Japanese Hiragana
  {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},          # Japanese Katakana
  {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},          # cjk radicals supplement
  {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
  {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
  {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
  {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
  {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
  {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
]


def is_cjk(char):
    # print(f"Is cjk? {char}")
    return len(char) == 1 and any([_range["from"] <= ord(char) <= _range["to"] for _range in CJK_RANGES])


# Splits a string into a list of words, but also accounts for CJK characters (which have no spaces in-between).
def split_cjk(string, sep_char=' '):
    ret = []
    while len(string) > 0:
        i = 0
        # print(string[i])
        # If the first character in string is CJK, set that to word.
        if is_cjk(string[i]):
            word = string[i]
        # Otherwise,
        else:
            # print("not cjk")
            word = ""
            # Loop through the string until the word ends or the end of the string is reached
            while i < len(string) and not is_cjk(string[i]):
                if string[i] == sep_char:  # If we find the separation,
                    i = i + 1  # still increment i, because we want to skip the separation char (but do not add to word)
                    break
                # print(f"adding {string[i]} to word")
                word += string[i]
                i += 1
            i -= 1

        ret.append(word)  # Add word to list
        string = string[i + 1:]  # Remove everything we've incremented over
    return ret


with open("Parameters.txt", encoding="utf8") as _in:
    parameters = _in.read()
parameters = parameters.split("\n")
parameters[1] = [i for i in parameters[1].split('"') if i != "" and i != " "]


RIGHT_SPACED = ['.', '-', ',', '!', '?', '—', ')']
LEFT_SPACED = ['(', '—']


for spaced in ['.', '-', ',', '!', '?', '(', '—', ')']:
    parameters[3] = parameters[3].replace(spaced, ' {0} '.format(spaced))

parameters[4] = int(parameters[4])

print(parameters)

corpus = ""
directory = parameters[0]
files_to_read = parameters[1]
# for file_name in files_to_read:
#     with open(directory + "/" + file_name, 'r') as _in:
#         corpus += _in.read()
for file_name in files_to_read:
    with open(directory + "/" + file_name, encoding="utf8") as _in:
        corpus += _in.read()
# print(corpus)


corpus = corpus.replace('\n', ' ')
corpus = corpus.replace('\t', ' ')
corpus = corpus.replace('“', ' " ')
corpus = corpus.replace('”', ' " ')
for spaced in ['.', '-', ',', '!', '?', '(', '—', ')']:
    corpus = corpus.replace(spaced, ' {0} '.format(spaced))
corpus_words = corpus.split(" ")
# corpus_words = corpus.split()
corpus_words = split_cjk(corpus)
corpus_words = [word for word in corpus_words if word != '']

print(corpus_words)
print(len(corpus_words))

distinct_words = list(set(corpus_words))
word_idx_dict = {word: i for i, word in enumerate(distinct_words)}
distinct_words_count = len(list(set(corpus_words)))

# k is adjustable
try:
    k = int(parameters[2])
except ValueError:
    k = 1
# Take the text k words at a time
sets_of_k_words = [' '.join(corpus_words[i:i+k]) for i, _ in enumerate(corpus_words[:-k])]
sets_of_k_words_count = len(list(set(sets_of_k_words)))

# Distinct sets
distinct_sets_of_k_words = list(set(sets_of_k_words))
# Give each distinct set of k words an identification number, an index (abbr. idx)
k_words_idx_dict = {word: i for i, word in enumerate(distinct_sets_of_k_words)}
print(k_words_idx_dict)

# the Markov chain
# I'M PRETTY SURE THE SECOND DECLARATION IS BETTER BUT I'LL KEEP THE FIRST COMMENTED JUST IN CASE
# next_after_k_words_matrix = dok_matrix((sets_of_k_words_count, len(distinct_words)))
next_after_k_words_matrix = dok_matrix((len(distinct_sets_of_k_words), len(distinct_words)))
# Loop through every set of k words and learn about which words follow each one
for i, k_words in enumerate(sets_of_k_words[:-k]):
    # Find the associated idx of the k words
    word_sequence_idx = k_words_idx_dict[k_words]
    # We are going in order, so we know the word following the ith group of k words is in the text at index [i + k]
    # Find it and its idx
    next_word_idx = word_idx_dict[corpus_words[i+k]]
    # Increment the group and word's associated cell
    next_after_k_words_matrix[word_sequence_idx, next_word_idx] += 1


def weighted_choice(choices, distribution):
    if len(choices) != len(distribution):
        raise ValueError(f"Expected equal number of choices and distributions: {len(choices)} != {len(distribution)}")
    sum = distribution.sum()
    if sum == 0:
        # print(distribution)
        return None
    r = randint(1, sum)
    cumm = 0
    for i in range(len(choices)):
        cumm += distribution[i]
        # print(cumm)
        if cumm >= r:
            # print("r: ", r, ", final i: ", i, ", which is ", choices[i], sep="")
            return choices[i]


def sample_next_word_after_sequence(word_sequence, alpha=0):
    next_word_vector = next_after_k_words_matrix.getrow(k_words_idx_dict[word_sequence]) + alpha
    likelihoods = next_word_vector  # / next_word_vector.sum()
    # print({index: elem for index, elem in enumerate(likelihoods.toarray()[0]) if elem != 0})
    return weighted_choice(distinct_words, likelihoods.toarray()[0])


def stochastic_chain(seed, chain_length=30, seed_length=k):
    current_words = split_cjk(seed)
    current_words = [word for word in current_words if word != '']  # current_words is always k words long
    next_word = current_words[-1]

    if len(current_words) != seed_length:
        raise ValueError(f'wrong number of words, expected {seed_length}, got {len(current_words)}, "{seed}"')
    sentence = seed

    count = 0
    for _ in range(chain_length):
        if not is_cjk(next_word):
            sentence += ' '
        next_word = sample_next_word_after_sequence(' '.join(current_words))
        try:
            sentence += next_word
        except TypeError:
            print(f"At iteration {_}, TypeError was hit (next_word was {next_word}, type {type(next_word)}).",
                  "It just means nothing was found to follow the last word.")
            print("The original word count has not been reached. I do not think anything went wrong.")
            break
        current_words = current_words[1:]+[next_word]
        # print(sentence, "\n")

        count += 1
    print("Counted words (including punctuation): ", count)
    return sentence


print("Prompt: ", parameters[3])
print([i for i in parameters[3].split(' ') if i != ''])
generated = stochastic_chain(parameters[3], parameters[4])

# remove space left
for sym in ['.', '-', ',', '!', '?', '—', ')']:
    generated = generated.replace(" " + sym, sym)
# remove space right
for sym in ['(', '—']:
    generated = generated.replace(sym + " ", sym)

# with open("out.txt", "w") as _out:
#     _out.write(generated)
with open("out.txt", encoding="utf8", mode="w+") as _out:
    _out.write(generated)



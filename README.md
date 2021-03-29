# AnalysisH-Project-Text-Generation
For Analysis H class, but is my further exploration of AI 

All the original code was from the following link:
https://towardsdatascience.com/markov-chains-how-to-train-text-generation-to-write-like-george-r-r-martin-cdc42786e4b6

I combined everything so it would work, but also added functionality for CJK (Chinese, Japanese, Korean) characters.

To use this, have another file containing all the input text. Write the the appropriate parameters as follows.

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

Larger k values create more accurate results but are less unique from the input text, so larger inputs combined with larger k values are ideal. (But, low k values are more entertaining to read.)

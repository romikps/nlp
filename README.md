# Direct translation enhanced by ngrams
In the current project, we implemented a direct translator enhanced by bigrams or trigrams. We also make use of POS tagging to choose more suitable translations, and then pluralize nouns, conjugate verbs and put adjectives in the comparative/superlative form if necessary to improve the quality of translations. Our main focus was to support translations from Italian, French, Spanish, German, Dutch to English, therefore the quality of those translations is expected to be higher compared to other language combinations.  
## Running the translator
- Navigate to project-improved-direct-translation
- In the command line run:

`python parsetree_translation.py (-f <text-file-to-translate> | -s <string-to-translate>) -src <language-to-translate-from> -trg <language-to-translate-to> [--bigram | --trigram]`

or

`python parsetree_translation.py (--file <text-file-to-translate> | --string <string-to-translate>) --source-language <language-to-translate-from> --target-language <language-to-translate-to> [--bigram | --trigram]`

from google_ngram_downloader import readline_google_store

fname, url, records = next(readline_google_store(ngram_len=1,indices='.'))
for x in range(0,5):
    print (next(records))
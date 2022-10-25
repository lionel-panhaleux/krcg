import urllib.request


for url in [
    "https://raw.githubusercontent.com/GiottoVerducci/vtescsv/main/vteslib.csv",
    "https://raw.githubusercontent.com/GiottoVerducci/vtescsv/main/vtescrypt.csv",
    "https://raw.githubusercontent.com/GiottoVerducci/vtescsv/main/vteslibmeta.csv",
    "https://raw.githubusercontent.com/GiottoVerducci/vtescsv/main/vtessets.csv",
]:
    target = "cards/" + url.rsplit("/", 1)[1]
    print(url, target)
    urllib.request.urlretrieve(url, target)

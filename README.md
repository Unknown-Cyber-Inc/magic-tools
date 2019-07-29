# magic_tools

A collection of Cythereal MAGIC clients to perform some special functions using capabilities exposed by the API.

## REQUIREMENTS

* `pip install -r requirements.txt`
* `export MAGIC_API_KEY="..."` with your API Key. 

## MAGIC Diff

To compute pairwise diff between binaries (identified by their sha1 hashes).

```
   python magic_diff.py hash1 hash2 hash3 ...
```

or give a file `hashes.txt` containing a list of hashes, one per line. (see `example-hashes.txt` for example)

```
  python magic_diff.py --lf hashes.txt
```

All hashes should be `sha1` compliant.

## NOTES

The scripts query MAGIC server for various dataset, such as genomics. Since this can take a long time, to aid 
repeated analysis using the same hashes, the scripts cache results in a local directory. Use `--help` to find the
default location of the cache, and parameter for overriding the default.

## TROUBLE SHOOTING TIPS

* The `hashes.txt` should be in Unix format. If working on Windows, use `dos2unix` to convert.
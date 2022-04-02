# Download movies from TVer.jp with title search

Downloading itself will be done by yt-dlp.

## How to install
If you are pkgsrc user, install the following packages.

* devel/py-requests
* net/yt-dlp
* security/py-cryptodome
* multimedia/ffmpeg4


## How to use
Collect URLs to track to download movies, for example in [URIs.txt](URIs.txt).

Run with `--gentitle`:

```
$ ./tver-downloader.py --gentitle URIs.txt titles.txt
```

You will get [titles.txt](titles.txt). This will be used more than one downloads.

Run without `--gentitle` periodically:

```
$ ./tver-downloader.py titles.txt
```

You will get .mp4 files in this directory.

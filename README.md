# Download movies from TVer.jp with title search

Downloading itself will be done by yt-dlp.

## How to install
If you are pkgsrc user, install thw following packages.

* www/py-beautifulsoup4
* devel/py-requests
* net/yt-dlp
* security/py-cryptodome
* multimedia/ffmpeg4


## How to use
Collect URLs to track to download movies, for example in [URI.txt](URI.txt).

Run with `--gentitle`:

```
$ ./tver-downloader.py --gentitle URI.txt titles.txt
```

You will get [titles.txt](titles.txt). This will be used more than one downloads.

Run without `--gentitle` periodically:

```
$ ./tver-downloader.py titles.txt
```

You will get .mp4 files in this directory.

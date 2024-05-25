# searpl

searpl is a small php search engine with the following features:

- [x] robot.txt compliant
- [x] sqlite, so theres no need to run some fancy database daemon
- [x] javascript not required
- [x] no cdns!
- [x] read-only database, nothing is written except with the shell

## licensing
searpl is licensed under an MIT licence, see [LICENSE](LICENSE)
for more information

## setup
this guide assumes you have shell access and are comfortable
using command line tools like git.

- make sure you have php, php-sqlite, wget, sqlite3 and git installed
- go in your `htdocs`, `public_html` or whatever and git clone
  this repo
- copy the contents of `create.sql` and paste it into the prompt
  on `sqlite3 db.sqlite` to create the database

optionally, if you want search ranking that prioritizes smol sites:

- build `searplrank.so` by running `make`
- in your `php.ini`, make sure `sqlite3.extension_dir` is uncommented
  and set to somewhere reasonable
- copy `searplrank.so` to wherever you set the extension_dir to

## crawling
the new crawler requires python3 and lxml

to index a page, feed it the database and some urls
```
python3 -m searplbot db.sqlite [some url]
```

the -c flag can be used to enable crawling and specify how many
connections to make before exiting


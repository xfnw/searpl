wget --spider --force-html -r -l1 -H -U 'searplbot/1.0' $@ 2>&1 | tee wg

grep '^--' wg | awk '{ print $3 }' \
  | grep -v '\.\(css\|js\|png\|gif\|jpg\|txt\|ico\|ttf\|svg\)$' \
  | tee ur

sleep 10

php crawl.php $(cat ur | shuf)

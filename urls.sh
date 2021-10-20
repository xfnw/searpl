wget -w 2 --random-wait --spider --force-html --tries 1 --timeout 2 -r -l1 -H -U 'searplbot/1.0' $@ 2>&1 | tee -a wg

grep '^--' wg | awk '{ print $3 }' \
  | grep -v '\.\(css\|js\|png\|gif\|jpg\|txt\|ico\|ttf\|svg\)$' \
  | sort | uniq \
  | tee -a ur

rm wg

sleep 10

php crawl.php $(cat ur | shuf)

rm ur



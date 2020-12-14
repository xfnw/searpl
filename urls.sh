wget --spider --force-html -r -l1 -H $@ 2>&1 \
  | grep '^--' | awk '{ print $3 }' \
  | grep -v '\.\(css\|js\|png\|gif\|jpg\|txt\|ico\|ttf\)$'

<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

$db = new PDO("sqlite:db.sqlite");



$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING );
//$stmt = $db->prepare($sql);
//$stmt->execute($params);

    function page_title($fp) {
        $res = preg_match("/<title>(.*)<\/title>/siU", $fp, $title_matches);
        if (!$res) 
            return null; 

        // Clean up title: remove EOL's and excessive whitespace.
        $title = preg_replace('/\s+/', ' ', $title_matches[1]);
        $title = trim($title);
        return $title;
    }



$arg = $argv;
array_shift($arg);

foreach ($arg as $url) {
	echo "\n";
	$url = preg_replace('/\/$/','',$url);
	echo $url."\n";

	$stmt = $db->prepare('DELETE FROM indexed WHERE url = ?');
	$stmt->execute([$url]);

	$file = file_get_contents($url);
	if (!$file)
		continue;
	$title = page_title($file);
	$document = preg_replace('/[ \t]+/', ' ', preg_replace('/[\r\n]+/', " ", strip_tags(preg_replace('/<(script|style)>(.*)<\/\1>/siU', ' ',$file))));
	if (!$title || !$document) {
		echo "no title!\n";
		continue;
	}

	echo "title: ".$title."\n";
echo $document;
	$stmt = $db->prepare('INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)');
	$stmt->execute([$title, $url, $document]);
}

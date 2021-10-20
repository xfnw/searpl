<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

$db = new PDO("sqlite:db.sqlite");

$context = stream_context_create(
    array(
        'http' => array(
            'follow_location' => false,
            'timeout' => 2,
            'user_agent' => 'searplbot/1.0'
        )
    )
);

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
	echo $url."\n";

	$stmt = $db->prepare('DELETE FROM indexed WHERE url = ?');
	$stmt->execute([htmlspecialchars(htmlspecialchars_decode($url))]);

	$file = file_get_contents($url, false, $context);
	if (!$file || strpos($http_response_header[0],'200 OK') === false)
		continue;
	$title = page_title($file);
	$document = preg_replace('/[ \t]+/', ' ', preg_replace('/[\r\n]+/', " ", strip_tags(preg_replace('/<(script|style)>(.*)<\/\1>/siU', ' ',$file))));
	if (!$title || !$document) {
		echo "no title!\n";
		continue;
	}

	echo "title: ".$title."\n";

	$stmt = $db->prepare('INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)');
	$stmt->execute([htmlspecialchars(htmlspecialchars_decode($title)), htmlspecialchars(htmlspecialchars_decode($url)), htmlspecialchars(htmlspecialchars_decode($document))]);
}

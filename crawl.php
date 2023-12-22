<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

$db = new SQLite3("db.sqlite", SQLITE3_OPEN_READWRITE);

$context = stream_context_create(
	array(
		'http' => array(
			'follow_location' => false,
			'timeout' => 2,
			'user_agent' => 'searplbot/1.0'
		)
	)
);

// FIXME: use an actual html parser?
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

$trunc = 0;
$prefix = '';
if (array_key_exists(0,$argv) && strlen($arg[0]) > 1 && $arg[0][0]=='-') {
	$trunc = (int)substr(array_shift($arg),1);
	$prefix = array_shift($arg);
}

foreach ($arg as $url) {
	$turl = $prefix.substr($url, $trunc);
	echo "\n".$turl."\n";

	$stmt = $db->prepare('DELETE FROM indexed WHERE url = ?');
	$stmt->bindValue(1, htmlspecialchars(htmlspecialchars_decode($url)));
	$stmt->execute();

	$file = file_get_contents($url, false, $context, 0, 1000000);
	if (!$file || isset($http_response_header) && strpos($http_response_header[0],'200 OK') === false)
		continue;
	$title = page_title($file);
	$document = preg_replace('/[ \t]+/', ' ', preg_replace('/[\r\n]+/', " ", strip_tags(preg_replace('/<(script|style)>(.*)<\/\1>/siU', ' ',$file))));
	if (!$title || !$document) {
		echo "no title!\n";
		continue;
	}

	echo "title: ".$title."\n";

	$stmt = $db->prepare('INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)');
	$stmt->bindValue(1, htmlspecialchars(str_replace('&mdash;','—',htmlspecialchars_decode($title))));
	$stmt->bindValue(2, htmlspecialchars(str_replace('&mdash;','—',htmlspecialchars_decode($turl))));
	$stmt->bindValue(3, htmlspecialchars(str_replace('&mdash;','—',htmlspecialchars_decode($document))));
	$stmt->execute();
}

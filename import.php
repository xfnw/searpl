<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

$arg = $argv;
array_shift($arg);

$db = new SQLite3("db.sqlite", SQLITE3_OPEN_READWRITE);
$dbin = new SQLite3(array_shift($arg), SQLITE3_OPEN_READWRITE);

$fromtable = array_shift($arg);

// XXX: do not give this untrusted input
$inp = $dbin->query('SELECT title,url,content FROM '.$fromtable);

while ($row = $inp->fetchArray()) {
	[$title, $url, $content] = $row;

	$document = preg_replace('/[ \t]+/', ' ', preg_replace('/[\r\n]+/', " ", strip_tags(preg_replace('/<(script|style)[^>]*>(.*)<\/\1>/siU', ' ',$content))));

	echo "title: ".$title."\n";

	$stmt = $db->prepare('INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)');
	$stmt->bindValue(1, str_replace('&mdash;','—',htmlspecialchars_decode($title)));
	$stmt->bindValue(2, str_replace('&mdash;','—',htmlspecialchars_decode($url)));
	$stmt->bindValue(3, str_replace('&mdash;','—',htmlspecialchars_decode($document)));
	$stmt->execute();
}

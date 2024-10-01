<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);

$name = basename($_SERVER['SCRIPT_FILENAME'], '.php');
?>
<!DOCTYPE HTML>
<html lang="en">
<link rel="stylesheet" type="text/css" href="assets/style.css">
<meta name="viewport" content="width=device-width, initial-scale=1" /> 
<meta name="description" content="a search engine">
<title><?=$name?></title>

<div class='wrapper'>
<h1><?=$name?></h1>

<div class='box search-container'>
<form action="?">
<input type="text" placeholder="Search.." name="q" value="<?php if (isset($_GET['q'])) {echo htmlspecialchars($_GET['q']);} ?>" onfocus="this.select()" autofocus>
<button type="submit"><i class="icon-search"></i></button>
</form>
</div>

<?php
$db = new SQLite3($name.".sqlite", SQLITE3_OPEN_READONLY);

if (isset($_GET['q']) && preg_replace('/\s+/', '', $_GET['q']) != '') {
	$sql = "SELECT title,url,snippet(indexed,2,'','','...',15) as snippet FROM indexed WHERE indexed MATCH ? ORDER BY rank LIMIT 1000";
	
	$stmt = $db->prepare($sql);
	$stmt->bindValue(1, $_GET['q']);

	set_error_handler(function ($_,$msg) {echo '<div class="box">'.substr($msg,65).'. you may want to view <a href="https://www.sqlite.org/fts5.html#full_text_query_syntax">this documentation</a> on writing valid queries.</div>';}, E_WARNING);
	$res = $stmt->execute();
	restore_error_handler();

	$results = false;
	if ($res) while ($row = $res->fetchArray()) {
		$results = true;
?>

<div class='box'>
<a href="<?php echo htmlspecialchars($row['url'], ENT_QUOTES); ?>"><?php echo htmlspecialchars($row['title']); ?></a>
<br>
<small><?php echo htmlspecialchars($row['url']); ?></small>
<br>
<?php
		echo htmlspecialchars($row['snippet']);
?>
</div>
<?php

	}
	if (!$results)
		echo '<div class="box">No results.</div>';

}
?>
</div>


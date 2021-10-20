<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);
?>
<!DOCTYPE HTML>
<html lang="en">
<link rel="stylesheet" type="text/css" href="assets/style.css">
<meta name="viewport" content="width=device-width, initial-scale=1" /> 
<meta name="description" content="a search engine">
<title>searpl</title>

<div class='wrapper'>
<h1>searpl</h1>

<div class='box search-container'>
<form action="./">
      <input type="text" placeholder="Search.." name="q" value="<?php if (isset($_GET['q'])) {echo htmlspecialchars($_GET['q']); } ?>">
      <button type="submit"><i class="icon-search"></i></button>
    </form>
</div>

<?php
$db = new PDO("sqlite:db.sqlite");
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING );

if (isset($_GET['q']) && preg_replace('/\s+/', '', $_GET['q']) != '') {

	$sql = "SELECT title,url,snippet(indexed,2,'<b>','</b>','...',15) as snippet FROM indexed WHERE indexed MATCH ? ORDER BY bm25(indexed,2,2,1)";
	$params = [$_GET['q']];
	
	$stmt = $db->prepare($sql);

	set_error_handler(function ($_,$msg) {echo '<div class="box">'.substr($msg,65).'. you may want to view <a href="https://www.sqlite.org/fts5.html#full_text_query_syntax">this documentation</a> on writing valid queries.</div>';}, E_WARNING);
	$stmt->execute($params);
	restore_error_handler();

	$results = false;
	while ($row = $stmt->fetch()) {
		$results = true;
?>

<div class='box'>
<a href="<?php echo $row['url']; ?>"><?php echo $row['title']; ?></a>
<br>
<small><?php echo $row['url']; ?></small>
<br>
<?php
		echo $row['snippet'];
?>
</div>
<?php

	}
	if (!$results)
		echo '<div class="box">No results.</div>';

} else {
?>

<div class='box'>
<h2>welcome to searpl</h2>
i am a simple, <a href='https://github.com/xfnw/searpl'>open source</a> search
engine that can find stuff :3
</div>

<div class='box'>
queries use <a href='https://www.sqlite.org/fts5.html#full_text_query_syntax'>FTS syntax</a>.
</div>

<div class='box'>
i have
<strong>
<?php
echo $db->query('SELECT rowid FROM indexed ORDER BY rowid DESC LIMIT 1')->fetchColumn();
?>
</strong> pages indexed, using <strong>
<?php
echo round(filesize('db.sqlite')/1024/1024);
?>
</strong>mb of storage
</div>
<?php
}
?>
</div>


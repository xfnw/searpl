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

	$sql = 'SELECT * FROM indexed WHERE 1=1';

	$terms = explode(' ', trim(preg_replace('/\s+/', ' ', $_GET['q'])));
	$params = array();
	foreach ($terms as $term) {
		if (substr($term, 0, 1) == '-') {

			$sql = $sql . ' AND content NOT LIKE ?';
			array_push($params,'%'.substr($term,1).'%');
		} else {

			$sql = $sql . ' AND content LIKE ?';
			array_push($params,'%'.$term.'%');
		}
	}
	$sql = $sql . ';';
	
	$stmt = $db->prepare($sql);
	$stmt->execute($params);


	$rows = array();
	$scores = array();
	while ($row = $stmt->fetch()) {
		$score = 0;
		foreach ($terms as $param)
			$score = $score + 100*(substr_count(strtolower($row['content']),strtolower($param)) / strlen($row['content']));
			$score = $score + 5000*(substr_count(strtolower($row['url']),strtolower($param)) / strlen($row['url']));
			$score = $score + 3000*(substr_count(strtolower($row['title']),strtolower($param)) / strlen($row['title']));
		array_push($scores, $score);
		$row['score'] = $score;
		array_push($rows, $row);
	}
	array_multisort($scores, SORT_DESC, $rows);

	$results = false;
	foreach ($rows as $row) {
		$results = true;
?>

<div class='box'>
<a href="<?php echo htmlspecialchars($row['url']); ?>"><?php echo htmlspecialchars($row['title']); ?></a>
<br>
<small>(score: <?php echo round($row['score']); ?>) <?php echo htmlspecialchars($row['url']); ?></small>
<br>
...<?php
		$content = $row['content'];
		foreach ($terms as $param) {
			$pos = strpos(strtolower($content), strtolower($param));
			if ($pos !== false) {
				echo htmlspecialchars(substr($content,$pos-50,50));
				echo '<strong>'.htmlspecialchars($param).'</strong>';
				echo htmlspecialchars(substr($content,$pos+strlen($param),50)).'...';
			}
		}

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
i am an <a href='https://github.com/xfnw/searpl'>open source</a> search
engine that can find stuff :3
</div>

<div class='box'>
normal words inputted will be tags, a -tag will blacklist the tag and
there is also unsorted SQL LIKE syntax.
<br>
more stuff like site: coming soon!
</div>

<div class='box'>
i have
<strong>
<?php
echo $db->query('SELECT id FROM indexed ORDER BY id DESC LIMIT 1')->fetchColumn();
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


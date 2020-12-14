<?php
ini_set('display_errors', '1');
ini_set('display_startup_errors', '1');
error_reporting(E_ALL);
?>
<!DOCTYPE HTML>
<html lang="en">
<link rel="stylesheet" type="text/css" href="assets/style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<meta name="viewport" content="width=device-width, initial-scale=1" /> 
<meta name="description" content="a search engine">
<title>searpl</title>

<div class='wrapper'>
<h1>searpl</h1>

<div class='box search-container'>
<form action="./">
      <input type="text" placeholder="Search.." name="q" value="<?php if (isset($_GET['q'])) {echo htmlspecialchars($_GET['q']); } ?>">
      <button type="submit"><i class="fa fa-search"></i></button>
    </form>
</div>

<?php

if (isset($_GET['q']) && preg_replace('/\s+/', '', $_GET['q']) != '') {
	$db = new PDO("sqlite:db.sqlite");

	$sql = 'SELECT * FROM indexed WHERE 1=1';

	$terms = explode(' ', preg_replace('/\s+/', '', $_GET['q']));
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
	
	$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING );
	$stmt = $db->prepare($sql);
	$stmt->execute($params);

	$results = false;
	while ($row = $stmt->fetch()) {
		$results = true;
?>

<div class='box'>
<a href="<?php echo htmlspecialchars($row['url']); ?>"><?php echo htmlspecialchars($row['title']); ?></a>
<br>
...<?php
		$content = $row['content'];
		foreach ($terms as $param) {
			$pos = strpos($content, $param);
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

}
?>
</div>


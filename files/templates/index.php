<?php

// Hello {{ groupname }}!
//
// This is your first PHP page that proves that everything works just fine.
//

todo: fixme;

// http://12factor.net/
$mysql = [
    "host" => $_SERVER["MYSQL_HOST"],
    "port" => $_SERVER["MYSQL_PORT"],
    "dbname" => $_SERVER["MYSQL_DB"],
    "username" => $_SERVER["MYSQL_USER"],
    "password" => $_SERVER["MYSQL_PASS"]
];

$conn = new PDO("mysql:host={$mysql['host']};".
                "port={$mysql['port']};dbname={$mysql['dbname']}",
                $mysql["username"], $mysql["password"]);

echo "<!-- All the tables:\n";
foreach ($conn->query("SHOW TABLES;") as $row) {
  echo "  " . $row[0] . "\n";
}
echo "-->\n\n";

phpinfo();

{# vim: set ft=jinja enc=utf-8: #}

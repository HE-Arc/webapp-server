<?php
{# vim: set ft=jinja: -#}

// Hello {{ groupname }}!
//
// This is your first PHP page that proves that everything works just fine.
//

todo: fixme;

// http://12factor.net/
$mysql = [
    "host" => $_SERVER["MYSQL_HOST"],
    "port" => $_SERVER["MYSQL_PORT"],
    "dbname" => $_SERVER["MYSQL_DATABASE"],
    "username" => $_SERVER["MYSQL_USERNAME"],
    "password" => $_SERVER["MYSQL_PASSWORD"]
];
// Hide it from phpinfo.
unset($_SERVER["MYSQL_PASSWORD"]);

$conn = new PDO("mysql:host={$mysql['host']};".
                "port={$mysql['port']};dbname={$mysql['dbname']}",
                $mysql["username"], $mysql["password"]);

echo "<!-- All the tables:\n";
foreach ($conn->query("SHOW TABLES;") as $row) {
  echo " -  " . $row[0] . "\n";
}
echo "-->\n\n";

phpinfo();

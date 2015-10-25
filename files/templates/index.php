<?php
{# vim: set ft=jinja: -#}

// Hello {{ groupname }}!
//
// This is your first PHP page that proves that everything works just fine.
//

// Xdebug is on.
todo: fixme;

// The configuration comes from the environment.
// See: http://12factor.net/
$mysql = [
    "host" => $_SERVER["MYSQL_HOST"],
    "port" => $_SERVER["MYSQL_PORT"],
    "dbname" => $_SERVER["MYSQL_DATABASE"],
    "username" => $_SERVER["MYSQL_USERNAME"],
    "password" => $_SERVER["MYSQL_PASSWORD"]
];

$pgsql = [
    "host" => $_SERVER["POSTGRES_HOST"],
    "port" => $_SERVER["POSTGRES_PORT"],
    "dbname" => $_SERVER["POSTGRES_DATABASE"],
    "username" => $_SERVER["POSTGRES_USERNAME"],
    "password" => $_SERVER["POSTGRES_PASSWORD"]
];


// Hide the passwords from phpinfo.
unset($_SERVER["MYSQL_PASSWORD"]);
unset($_SERVER["POSTGRES_PASSWORD"]);

// MySQL
$conn = new PDO("mysql:host={$mysql['host']};".
                "port={$mysql['port']};dbname={$mysql['dbname']}",
                $mysql["username"], $mysql["password"]);
echo "<!-- All the MySQL tables:\n";
foreach ($conn->query("SHOW TABLES;") as $row) {
    echo " -  " . $row[0] . "\n";
}
echo "-->\n\n";

// Postgres
$conn = new PDO("pgsql:host={$pgsql['host']};".
                "port={$pgsql['port']};dbname={$pgsql['dbname']}",
                $pgsql["username"], $pgsql["password"]);

echo "<!-- All the PostgreSQL tables:\n";
foreach ($conn->query("select tablename from pg_tables") as $row) {
    echo " -  " . $row[0] . "\n";
}
echo "-->\n\n";

// Sending emails
mail("test@test.com", "Test", "Hello World!");

// Le PHP info.
phpinfo();

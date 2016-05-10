<?php
{# vim: set ft=jinja: -#}

// Hello {{ groupname }}!
//
// This is your first PHP page that proves that everything works just fine.
//

// Xdebug is on.
todo: fixme;

mb_internal_encoding("utf-8");

// The configuration comes from the environment.
// See: http://12factor.net/
$mysql = [
    "host" => "mysql",
    "port" => 3306,
    "dbname" => $_SERVER["MYSQL_USERNAME"],
    "username" => $_SERVER["MYSQL_USERNAME"],
    "password" => $_SERVER["MYSQL_PASSWORD"]
];

$pgsql = [
    "host" => "postgres",
    "port" => 5432,
    "dbname" => $_SERVER["POSTGRES_USERNAME"],
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
$conn->exec("SET search_path TO production;");

echo "<!-- All the PostgreSQL tables:\n";
foreach ($conn->query("select tablename from pg_tables") as $row) {
    echo " -  " . $row[0] . "\n";
}
echo "-->\n\n";

// Memcached
$memcache = new Memcached();
$memcache->addServer($_SERVER["MEMCACHED_HOST"], (int) $_SERVER["MEMCACHED_PORT"]);
$memcache->set("foo", 1);
$memcache->increment("foo");
echo "<!-- Memcache: " . $memcache->get("foo") . "-->\n\n";

// Redis
$redis = new Redis();
$redis->connect($_SERVER["REDIS_HOST"], (int) $_SERVER["REDIS_PORT"]);
echo "<!-- Redis: " . $redis->ping() . " -->\n\n";

// Sending emails
mail("test@test.com", "Test", "Hello World!");

// Le PHP info.
phpinfo();

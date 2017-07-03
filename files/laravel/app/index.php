<?php

// Hello!
//
// This is your first PHP page that proves that everything works just fine.
//

// Xdebug is on.
todo: fixme;

mb_internal_encoding("utf-8");

// The configuration comes from the environment.
// See: http://12factor.net/
$mysql = [
    "host" => $_SERVER["MYSQL_HOST"],
    "port" => $_SERVER["MYSQL_PORT"],
    "dbname" => $_SERVER["GROUPNAME"],
    "username" => $_SERVER["GROUPNAME"],
    "password" => $_SERVER["PASSWORD"]
];

$pgsql = [
    "host" => $_SERVER["POSTGRES_HOST"],
    "port" => $_SERVER["POSTGRES_PORT"],
    "dbname" => $_SERVER["GROUPNAME"],
    "username" => $_SERVER["GROUPNAME"],
    "password" => $_SERVER["PASSWORD"]
];


// Hide the secrets from phpinfo.
foreach(["PASSWORD", "SECRET_KEY", "SECRET_KEY_BASE"] as $secret) {
  unset($_SERVER[$secret]);
  unset($_ENV[$secret]);
  putenv("$secret=");
  putenv($secret);
}

// MySQL
try {
  $conn = new PDO("mysql:host={$mysql['host']};".
                  "port={$mysql['port']};dbname={$mysql['dbname']}",
                  $mysql["username"], $mysql["password"]);
  echo "<!-- All the MySQL tables:\n";
  foreach ($conn->query("SHOW TABLES;") as $row) {
      echo " -  " . $row[0] . "\n";
  }
  echo "-->\n\n";
} catch(PDOException $e) {
  echo "<pre><code>MySQL: " . $e->getMessage() . " </code></pre>\n\n";
}

// Postgres
try {
  $conn = new PDO("pgsql:host={$pgsql['host']};".
                  "port={$pgsql['port']};dbname={$pgsql['dbname']}",
                  $pgsql["username"], $pgsql["password"]);
  $conn->exec("SET search_path TO production;");

  echo "<!-- All the PostgreSQL tables:\n";
  foreach ($conn->query("select tablename from pg_tables") as $row) {
      echo " -  " . $row[0] . "\n";
  }
  echo "-->\n\n";
} catch(PDOException $e) {
  echo "<pre><code>Postgres: " . $e->getMessage() . " </code></pre>\n\n";
}

// Redis
try {
  $redis = new Redis();
  $redis->connect($_SERVER["REDIS_HOST"], (int) $_SERVER["REDIS_PORT"]);
  echo "<!-- Redis: " . $redis->ping() . " -->\n\n";
} catch(RedisException $e) {
  echo "<pre><code>Redis: " . $e->getMessage() . " </code></pre>\n\n";
}

// Sending emails
mail(
  "no-reply@example.org",
  gethostname(),
  "Hello World!"
);

// Le PHP info.
phpinfo();

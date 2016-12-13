#!/usr/bin/env python3
"""
Database creation
-----------------

Sets up all the databases
"""

import os
import sys
import yaml
import subprocess
import tempfile

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.3.0"

# Database host
hostname = "127.0.0.1"
# Root password
root = "root"

mysql = r"""
    DROP USER IF EXISTS `{username}`;
    DROP DATABASE IF EXISTS `{database}`;
    DROP DATABASE IF EXISTS `{database}_production`;
    DROP DATABASE IF EXISTS `{database}_test`;
    CREATE USER '{username}'@'%';
    SET PASSWORD FOR '{username}'@'%' = PASSWORD('{password}');
    CREATE DATABASE `{database}` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE `{database}_production` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE `{database}_test` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON `{database}`.* TO '{username}'@'%';
    GRANT ALL PRIVILEGES ON `{database}_production`.* TO '{username}'@'%';
    GRANT ALL PRIVILEGES ON `{database}_test`.* TO '{username}'@'%';
    FLUSH PRIVILEGES;
"""

postgresql = r"""
    DROP DATABASE IF EXISTS {database};
    DROP ROLE IF EXISTS {username};
    CREATE ROLE {username} WITH NOINHERIT LOGIN PASSWORD '{password}' VALID UNTIL 'infinity';
    CREATE DATABASE {database} WITH ENCODING 'UTF8' OWNER {username};
    REVOKE ALL PRIVILEGES ON DATABASE {database} FROM public;
    GRANT ALL PRIVILEGES ON DATABASE {database} TO {username};
"""

postgresql_schema = r"""
    DROP SCHEMA IF EXISTS public;
    CREATE SCHEMA {username} AUTHORIZATION {username};
    CREATE SCHEMA production AUTHORIZATION {username};
    CREATE SCHEMA test AUTHORIZATION {username};
"""


def main(argv):
    compose_file = argv[1]

    with open(compose_file, "r", encoding="utf-8") as f:
        compose = yaml.load(f)

        for machine, description in compose['services'].items():
            if 'hostname' not in description:
                continue

            groupname = description['environment']['GROUPNAME']
            password = description['environment']['PASSWORD']

            print(groupname)
            print("=" * len(groupname))

            p = subprocess.Popen(
                ['mysql', '-h', hostname, '-u', 'root', '-p{}'.format(root)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            stdin = mysql.format(
                username=groupname, password=password,
                database=groupname).strip()

            out, err = p.communicate(bytearray(stdin, 'utf-8'))
            if p.returncode != 0:
                print(err.decode('utf-8'), end='', file=sys.stderr)
            else:
                print("MySQL databases created.")
                #print(out.decode('utf-8'), end='')

            with tempfile.NamedTemporaryFile() as fp:
                fp.write(
                    bytearray('{}:*:*:postgres:{}'.format(hostname, root),
                              'utf-8'))
                fp.seek(0)
                os.chmod(fp.name, mode=0o600)

                env = os.environ.copy()
                env['PGPASSFILE'] = fp.name

                commands = (
                    ('database', ('psql', '-h', hostname, '-U', 'postgres'),
                     postgresql), ('schemas', ('psql', '-h', hostname, '-U',
                                               'postgres', '-d', groupname),
                                   postgresql_schema))

                for txt, command, stdin in commands:
                    p = subprocess.Popen(
                        command,
                        env=env,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

                    stdin = stdin.format(
                        username=groupname,
                        password=password,
                        database=groupname).strip()

                    out, err = p.communicate(bytearray(stdin, 'utf-8'))
                    if p.returncode != 0:
                        print(err.decode('utf-8'), end='', file=sys.stderr)
                    else:
                        print("Postgresql {} created.".format(txt))
                        #print(out.decode('utf-8'), end='')

            print("")


if __name__ == "__main__":
    sys.exit(main(sys.argv))

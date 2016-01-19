#!/usr/bin/env python3
"""
Github keys
-----------

Downloads the ssh keys from github.
"""

import os
import csv
import sys
import requests

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.1.0"


def github(username, auth):
    output = []
    # Create authorized_keys
    r = requests.get("https://api.github.com/users/{}/keys".format(username),
                     auth=auth)
    if r.ok:
        keys = r.json()
        for key in keys:
            output.extend((key["key"], " ", username, "@", str(key["id"]), "\n"))
        sys.stdout.write("Key of {}\n".format(username))

    else:
        sys.stderr.write("\nCannot grab github key of {}\n".format(username))
        return None

    return "".join(output)


def main(argv):
    students = argv[1]
    destination = argv[2]
    github_user = argv[3]
    github_key = argv[4]

    with open(students, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        # skip headers
        next(reader)
        for row in reader:
            username = row[7]
            if not username:
                continue

            key = os.path.join(destination, "{}.key".format(username))
            if not os.path.exists(key) and not username.endswith(".isic"):
                content = github(username, (github_user, github_key))
                if (content):
                    with open(key, "w+") as g:
                        g.write(content)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

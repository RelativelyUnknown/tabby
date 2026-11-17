#!/usr/bin/env bash
# Builds the fixture project for the `keyword-categoriser-near-miss` case in the empty workspace.
set -euo pipefail
printf 'Datum;Omschrijving;Bedrag\n20260902;Rent Mr Jansen;950,00\n20260903;Albert Heijn Utrecht;23,45\n20260904;Current account fee;1,50\n20260905;Caf\xe9 de Leon;12,00\n' > export.csv
git init -q -b main
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -qm base

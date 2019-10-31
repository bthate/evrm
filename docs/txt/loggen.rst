.. _loggen:

LOGGEN
######

"Het bewust gebruikerschap mag niet onthouden worden."

Je kan het log command gebruiken om te registreren:

| log <txt>
| log <txt> +5
| log <txt> -2

Het find command om log terug te zoeken:

| find log
| find log=wakker
| find email From=om.nl From Subject Date start=2013-01-01 end=2013-02-01

Om over een periode te kunnen zoeken:

| today log
| week log
| week log=wiet
| week log=wakker

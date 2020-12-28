DROP USER moneyflows;

CREATE USER moneyflows
IDENTIFIED BY WELcome11##
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

GRANT connect, resource, graph_developer TO moneyflows;

EXIT

DROP USER moneyflows;

CREATE USER moneyflows
IDENTIFIED BY WELcome123##
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

GRANT
  create session
, create table
, create view
, graph_developer
, pgx_session_add_published_graph
TO moneyflows;

EXIT

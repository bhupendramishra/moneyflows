# money-tranfer

## Create dataset

Run the python script to create graph with the number of accounts.

    $ cd data/
    $ python3 create_graph.py 10000

This script creates 3 CSV files.

    $ ls *.csv
    account.csv customer.csv transaction.csv

## Load dataset to tables

Run a bash console on `database` container as user "54321" (= "oracle" user in the container, for writing the sqlldr files).

    $ docker-compose exec --user 54321 database /bin/bash

Move to the project directory (inside the container).

    $ cd /graphs/moneyflows/script/

Create a database user.

    $ sqlplus sys/Welcome1@orclpdb1 as sysdba @create-user.sql

Create tables.

    $ sqlplus moneyflows/WELcome11##@orclpdb1 @create-table.sql

Load the data from the CSV file.

    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_acc.ctl direct=true
    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_cst.ctl direct=true
    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_txn.ctl direct=true

Exit from the database container.

    $ exit

## Create property graph

Then start a client shell instance that connects to the server

    $ docker-compose exec graph-client opgpy --base_url http://graph-server:7007 --user moneyflows
    
    enter password for user hackmakers (press Enter for no password): WELcome11##
    
    Oracle Graph Server Shell 20.4.0
    >>>

Set the create property graph statement.

[`create-pg.pgql`](script/create-pg.pgql)

    >>> statement = open('/graphs/moneyflows/script/create-pg.pgql', 'r').read()

Run the statement.

    >>> session.prepare_pgql(statement).execute()
    False

Get the created graph and try a PGQL query.

    >>> graph = session.get_graph("Moneyflows")
    >>> graph.query_pgql("""
            SELECT a1.acc_id AS a1_acc_id, t.datetime, t.amount, a2.acc_id AS a2_acc_id
            FROM MATCH (a1)-[t:transferred_to]->(a2)
            LIMIT 5
        """).print()

If you need to recreate the graph, destroy the graph first and run the statement above again.

    >>> graph.destroy()

To make this graph accessable from other sessions, publish the graph.

    >>> graph.publish()

## Run queries

If the graph is already published, other sessions can view it using Graph Visualization app.

    - http://localhost:7007/ui/

If the graph is not published, get the session ID to login with the same session and view the graph.

    >>> session
    PgxSession(id: 54935993-1d06-41a6-bf8e-efeab1aaf144, name: python_pgx_client)

### Simple fund tracing and entity relationships

```sql
SELECT *
FROM MATCH (c:customer)-[e:owns]->(a:account)
WHERE c.cst_id = 10
```

```sql
SELECT *
FROM MATCH (c:customer)-[e:owns]->(a1:account)-[t:transferred_to]-(a2:account)
WHERE c.cst_id = 10
```

### Cyclic Transactions

2-hops

```
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
WHERE a1.acc_id = 997
```

2-hops cycle

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a1)
WHERE a1.acc_id = 10
```

2-hops considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a1)
WHERE a1.acc_id = 100
AND t1.amount >= 500 AND t2.amount >= 500 AND t1.datetime < t2.datetime
```

3-hops considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
   , MATCH (a3)-[t3:transferred_to]->(a1)
WHERE a1.acc_id < 100
  AND t1.amount >= 500 AND t2.amount >= 500 AND t3.amount >= 500
  AND t1.datetime < t2.datetime AND t2.datetime < t3.datetime
```

4-hops considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
   , MATCH (a3)-[t3:transferred_to]->(a4)-[t4:transferred_to]->(a1)
WHERE a1.acc_id < 100 AND ID(a1) != ID(a3) AND ID(a2) != ID(a4)
  AND t1.amount >= 500 AND t2.amount >= 500 AND t3.amount >= 500 AND t4.amount >= 500
  AND t1.datetime < t2.datetime AND t2.datetime < t3.datetime AND t3.datetime < t4.datetime
```

Using PATH macro

```sql
PATH p AS ()-[:transferred_to]->(a) WHERE ID(a) != 10
SELECT *
FROM MATCH (a1)-/:p{2,5}/->(a)-[t:transferred_to]->(a1)
WHERE a1.acc_id = 10
```

Using PATH macro with conditions

```sql
PATH p AS ()-[t:transferred_to]->(a) WHERE ID(a) != 10 AND t.amount >= 800
SELECT *
FROM MATCH (a1)-/:p{2,5}/->(a)-[t:transferred_to]->(a1)
WHERE a1.acc_id = 10 AND t.amount >= 800
```

Using SHORTEST PATH

```sql
SELECT ARRAY_AGG(a.acc_id) AS list_of_accounts
     , ARRAY_AGG(ID(t))    AS list_of_transactions
     , ARRAY_AGG(t.amount) AS list_of_amounts
FROM MATCH TOP 100 SHORTEST ((a1) (-[t:transferred_to]->(a))* (a1))
WHERE a1.acc_id = 10
```

Show a cycle giving a list of transactions

```sql
SELECT *
FROM MATCH (a1)-[t]->(a2)
WHERE ID(t) IN (396, 235, 42, 527, 603)
```

Possible extension? (not yet supported)

```sql
SELECT ARRAY_AGG(a2.acc_id) AS list_of_accounts
     , ARRAY_AGG(ID(t1))    AS list_of_transactions
     , ARRAY_AGG(t1.amount) AS list_of_amounts
FROM MATCH TOP 100 SHORTEST (
        (a) (
            (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
            WHERE a1.acc_id != a3.acc_id
              AND t1.datetime < t2.datetime
              AND t1.amount >= 500 AND t2.amount >= 500
        )* (a)
    )
WHERE a.acc_id = 100

Not yet supported: multiple edge patterns in SHORTEST or CHEAPEST
```



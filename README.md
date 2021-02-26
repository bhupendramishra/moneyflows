# Moneyflows

- [Setup environment](#setup-environment)
- [Prepare dataset](#prepare-dataset)
- [Load dataset to tables](#load-dataset-to-tables)
- [Create property graph](#create-property-graph)
- [Publish graph](#publish-graph)
- [Visualize graph](#visualize-graph)
- [Run PGQL queries](#run-pgql-queries)

## Setup environment

Please follow the documentations below.

- [Oracle Cloud](https://github.com/rexzj266/oracle-pgx-on-dbcs-quickstart/blob/master/marketplace/pdx-deploy-from-marketplace.md)
- [Docker](https://github.com/ryotayamanaka/oracle-pg/blob/20.4/README.md)

## Download the scripts

### Oracle Cloud

Login to the **DBCS** instance and clone this repository at the home directory of `oracle` user.

    $ sudo su - oracle
    $ cd ~
    $ git clone https://github.com/ryotayamanaka/moneyflows.git

Login to the **Graph Server** instance and clone this repository at the home directory of `opc` user.

    $ cd ~
    $ git clone https://github.com/ryotayamanaka/moneyflows.git

### Docker

Go to `graphs/` directory and clone this repository.

    $ cd oracle-pg/graphs/
    $ git clone https://github.com/ryotayamanaka/moneyflows.git

## Prepare dataset

### Pre-created dataset

Sample dataset is under `/data/scale-100/` directory.

    $ ls /data/scale-100/*.csv
    account.csv customer.csv transaction.csv

Copy the 3 CSV files under `/data/` for loading.

    $ cp /data/scale-100/*.csv /data/

### Larger dataset (optional)

For creating a graph with larger number of accounts (e.g. 10000), run this script.

    $ cd script/
    $ python3 create_graph.py 10000

This script creates 3 CSV files.

    $ ls *.csv
    account.csv customer.csv transaction.csv

Locate the CSV files under `/data/` directory.

    $ mv *.csv ../data/

## Load dataset to tables

### Oracle Cloud

Move to `script/` directory.

    $ cd ~/moneyflows/script/

Create a database user.

    $ sqlplus sys/Welcome1@<pdb-service-name> as sysdba @create-user.sql

Create tables.

    $ sqlplus moneyflows/WELcome11##@<pdb-service-name> @create-table.sql

Load the data from the CSV file.

    $ sqlldr moneyflows/WELcome11##@<pdb-service-name> sqlldr_acc.ctl direct=true
    $ sqlldr moneyflows/WELcome11##@<pdb-service-name> sqlldr_cst.ctl direct=true
    $ sqlldr moneyflows/WELcome11##@<pdb-service-name> sqlldr_txn.ctl direct=true

Exit from the database container.

    $ exit

### Docker

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

    # Oracle Cloud (Graph Server)
    $ opgpy --base_url http://graph-server:7007 --user moneyflows
    
    # Docker
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

## Publish graph

To make this graph accessable from other sessions, you need to publish the graph.

Open the conf file and add the permission for publilshing graphs to the role.

    $ vi /etc/oracle/graph/pgx.conf

`pgx.conf`

    "pgx_role": "GRAPH_DEVELOPER",
    "pgx_permissions": [
      { "grant": "PGX_SESSION_CREATE" },
      { "grant": "PGX_SESSION_NEW_GRAPH" },
      { "grant": "PGX_SESSION_GET_PUBLISHED_GRAPH" },
      { "grant": "PGX_SESSION_ADD_PUBLISHED_GRAPH" },    <--

Restart the Graph Server.

    $ sudo systemctl restart pgx

Login to the Python shell, create the graph again, then publish it. 

    >>> graph.publish()

## Visualize graph

If the graph is already published, other sessions can view it using Graph Visualization app.

- Oracle Cloud: https://<ip_address>:7007/ui/
- Docker: http://localhost:7007/ui/

If the graph is not published, get the session ID to login with the same session and view the graph.

    >>> session
    PgxSession(id: 54935993-1d06-41a6-bf8e-efeab1aaf144, name: python_pgx_client)

Unzip [highlighs.json.zip](./highlighs.json.zip) and upload onto Graph Visualization UI.

## Run PGQL queries

- [Simple entity relationships](#simple-entity-relationships)
- [Cyclic transfers](#cyclic-transfers)
- [Path finding](#path-finding)
- [Aggregation and sort](#aggregation-and-sort)

### Simple entity relationships

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

2-hops transfer

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
WHERE a1.acc_id = 10
```

### Cyclic transfers

2-hops cycle

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a1)
WHERE a1.acc_id = 10
```

2-hops cycle considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a1)
WHERE a1.acc_id = 10
AND t1.amount >= 500 AND t2.amount >= 500 AND t1.datetime < t2.datetime
```

3-hops cycles considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
   , MATCH (a3)-[t3:transferred_to]->(a1)
WHERE a1.acc_id <= 50
  AND t1.amount >= 500 AND t2.amount >= 500 AND t3.amount >= 500
  AND t1.datetime < t2.datetime AND t2.datetime < t3.datetime
```

4-hops cycles considering amount and datetime

```sql
SELECT *
FROM MATCH (a1)-[t1:transferred_to]->(a2)-[t2:transferred_to]->(a3)
   , MATCH (a3)-[t3:transferred_to]->(a4)-[t4:transferred_to]->(a1)
WHERE a1.acc_id <= 10 AND ID(a1) != ID(a3) AND ID(a2) != ID(a4)
  AND t1.amount >= 500 AND t2.amount >= 500 AND t3.amount >= 500 AND t4.amount >= 500
  AND t1.datetime < t2.datetime AND t2.datetime < t3.datetime AND t3.datetime < t4.datetime
```

Using [PATH pattern macro](https://pgql-lang.org/spec/1.3/#path-pattern-macros)

```sql
PATH p AS ()-[:transferred_to]->(a) WHERE a.acc_id != 10
SELECT *
FROM MATCH (a1)-/:p{2,3}/->(a)-[t:transferred_to]->(a1)
WHERE a1.acc_id = 10
```

Using PATH pattern macro with conditions

```sql
PATH p AS ()-[t:transferred_to]->(a) WHERE a.acc_id != 10 AND t.amount >= 500
SELECT *
FROM MATCH (a1)-/:p{2,3}/->(a)-[t:transferred_to]->(a1)
WHERE a1.acc_id = 10 AND t.amount >= 500
```

Using [TOP K SHORTEST match](https://pgql-lang.org/spec/1.3/#top-k-shortest-path)

```sql
SELECT ARRAY_AGG(a.acc_id) AS list_of_accounts
     , ARRAY_AGG(ID(t))    AS list_of_transactions
     , ARRAY_AGG(t.amount) AS list_of_amounts
FROM MATCH TOP 100 SHORTEST ((a1) (-[t:transferred_to]->(a))* (a1))
WHERE a1.acc_id = 30
```

Show the cycle, giving a list of transfers

```sql
SELECT *
FROM MATCH (a1)-[t]->(a2)
WHERE ID(t) IN (150700, 50546, 136033, 200475)
```

### Path finding

```sql
SELECT *
FROM MATCH (a1)-[t1]-(a)-[t2]->(a2)
WHERE a1.acc_id = 10 AND a2.acc_id = 20
```

```sql
SELECT ARRAY_AGG(a.acc_id) AS list_of_accounts
     , ARRAY_AGG(ID(t))    AS list_of_transactions
     , MIN(t.amount)       AS min_amount_on_path
FROM MATCH TOP 100 SHORTEST ((a1) (-[t:transferred_to]->(a))* (a2))
WHERE a1.acc_id = 10 AND a2.acc_id = 30
ORDER BY MIN(t.amount) DESC
```

```sql
SELECT *
FROM MATCH (a1)-[t]->(a2)
WHERE ID(t) IN (150581, 15188, 176814, 144851)
```

### Aggregation and sort

Multiple remitters to single beneficiary with small amounts (<= 500.00) over a period of time.

List the beneficiaries who have received the top 10 most transfers.

```sql
SELECT a2.acc_id AS beneficiary_id, COUNT(a2) AS num_of_remitters
FROM MATCH (a1)-[t:transferred_to]->(a2)
WHERE t.datetime >= TIMESTAMP '2020-10-01 00:00:00'
  AND t.datetime < TIMESTAMP '2020-12-01 00:00:00'
  AND t.amount <= 500.00
GROUP BY a2 ORDER BY num_of_remitters DESC LIMIT 10
```

Visualize the top beneficiary and the transfers.

```sql
SELECT *
FROM MATCH (a1)-[t:transferred_to]->(a2)
WHERE t.datetime >= TIMESTAMP '2020-10-01 00:00:00'
  AND t.datetime < TIMESTAMP '2020-12-01 00:00:00'
  AND t.amount <= 500.00
  AND a2.acc_id = 33
```

### Appendix

Possible extension (not yet supported)

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



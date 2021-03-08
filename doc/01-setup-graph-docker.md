## Download the scripts

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

Run a bash console on `database` container as user "54321" (= "oracle" user in the container, for writing the sqlldr files).

    $ docker-compose exec --user 54321 database /bin/bash

Move to the project directory (inside the container).

    $ cd /graphs/moneyflows/script/

Create a database user.

    $ sqlplus sys/Welcome1@orclpdb1 as sysdba @create-user.sql

Create tables.

    $ sqlplus moneyflows/WELcome123##@orclpdb1 @create-table.sql

Load the data from the CSV file.

    $ sqlldr moneyflows/WELcome123##@orclpdb1 sqlldr_acc.ctl direct=true
    $ sqlldr moneyflows/WELcome123##@orclpdb1 sqlldr_cst.ctl direct=true
    $ sqlldr moneyflows/WELcome123##@orclpdb1 sqlldr_txn.ctl direct=true

Exit from the database container.

    $ exit

## Create property graph

Then start a client shell instance that connects to the server
    
    # Docker
    $ docker-compose exec graph-client opgpy --base_url http://graph-server:7007 --user moneyflows    
    enter password for user moneyflows (press Enter for no password): WELcome123##
    Oracle Graph Server Shell 21.1.0
    >>>

Set the create property graph statement.

[`create-pg.pgql`](script/create-pg.pgql)

    >>> statement = open('/graphs/moneyflows/script/create-pg.pgql', 'r').read()

Run the statement.

    >>> session.prepare_pgql(statement).execute()
    False

Get the created graph and try a PGQL query.

    >>> graph = session.get_graph("Moneyflows")
    >>> graph
    PgxGraph(name: Moneyflows, v: 180, e: 3100, directed: True, memory(Mb): 0)
    >>> graph.query_pgql("""
            SELECT a1.acc_id AS a1_acc_id, t.datetime, t.amount, a2.acc_id AS a2_acc_id
            FROM MATCH (a1)-[t:transferred_to]->(a2)
            LIMIT 5
        """).print()

If you need to recreate the graph, destroy the graph first and run the statement above again.

    >>> graph.destroy()

To make this graph accessable from other sessions, you need to publish the graph. The privilege to publish graphs (= `PGX_SESSION_ADD_PUBLISHED_GRAPH`) has been already granted when the user is created.

    >>> graph.publish()

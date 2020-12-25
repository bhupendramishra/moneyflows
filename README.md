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

    $ cd oracle-pg/
    $ docker-compose exec --user 54321 database /bin/bash

Move to the project directory (inside the container).

    $ cd /graphs/moneyflows/script/

Create a database user.

    $ sqlplus sys/Welcome1@orclpdb1 as sysdba @create_user.sql

Create tables.

    $ sqlplus moneyflows/WELcome11##@orclpdb1 @create_table.sql

Load the data from the CSV file.

    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_acc.ctl sqlldr.log sqlldr.bad direct=true
    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_cst.ctl sqlldr.log sqlldr.bad direct=true
    $ sqlldr moneyflows/WELcome11##@orclpdb1 sqlldr_txn.ctl sqlldr.log sqlldr.bad direct=true

Exit from the database container.

    $ exit

## Create property graph

Then start a client shell instance that connects to the server

    opgpy --base_url http://graph-server:7007 --user moneyflows
    
    enter password for user hackmakers (press Enter for no password): 
    
    Oracle Graph Server Shell 20.4.0
    >>>


Set the create property graph statement.


    statement = '''
    '''

Run the statement.

    session.prepare_pgql(statement).execute()

If you need to recreate the graph, destroy the graph first and run the statement above again.

    graph.destroy()

## Run queries



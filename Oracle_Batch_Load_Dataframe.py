


import pandas as pd
import numpy as np
import datetime
import sys
import re
from itertools import groupby, islice, takewhile
import cx_Oracle

format = '%y_%m_%d'

TODAY = datetime.date.today()
add = datetime.timedelta(days=1)
yesterday = datetime.date.today() - add
dd = datetime.date.strftime(TODAY,format)

# connection variables
connection = cx_Oracle.connect("user/Oracle_database_connect_info")
cur = connection.cursor()

# dataframe headers
columns = ['C1','C2','C3','C4']

# -- >> test and sample the file
csv_df = pd.read_csv(r'csvfile_location')

# add record_id for values
csv_df_idx = csv_df.index.values +1
csv_df.insert(0,column = 'RECORD_ID' , value=csv_df_idx)


### TABLE ALREADY CREATED IN DATABASE ###


# set batch size ie record count
batch_size = 100000

# create chunker function to separate the dataframe into batches
# Note: last batch will contain smallest amout of records.
def chunker(seq,size):
    return(seq[pos:pos+size] for pos in range(0,len(seq),size))


insert_statement = """
    INSERT INTO TEST_LOAD
        ( RECORD_ID ,C1 ,C2 ,C3 ,C4)values (:1,:2,:3,:4,:5)    """

# Optional use cursor.prepare so Oracle DB avoids compiling the insert statement over and over
try:
    cur.prepare(insert_statement)
except cx_Oracle.DatabaseError as Exception:
    printf('Failed to prepare insert cursor')
    printException(Exception)
    exit(1)

for i in chunker(csv_df,batch_size):
    ### Insert and Iterate to inset records
    ### Convert to list for easy load into DB
    csv_df_dataset_lst = csv_df.values.tolist()

    cur.executemany(insert_statement,csv_df_dataset_lst)
    connection.commit()
    # record counter to monitor the loading.
    number_of_records_loaded = cur.execute("""SELECT COUNT(*), SYSDATE FROM TEST_LOAD GROUP BY SYSDATE""")
    record_out = cur.fetchall()
    for row in record_out:
        print(row)
connection.close()
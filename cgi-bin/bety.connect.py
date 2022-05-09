#!/usr/bin/env python3

import psycopg2
import json
import cgi
import cgitb

print("Content-type: text/html\n")
#establishing the connection
conn = psycopg2.connect(
   database="bety", user='postgres', password='', host='127.0.0.1', port= '6543'
)

form = cgi.FieldStorage() 

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

pftid = form.getvalue("pft_id","")

query = "select pft_id, specie_id, scientificname  from pfts_species join species on (specie_id = species.id) where pft_id = %s limit 10"

#Executing an MYSQL function using the execute() method
cursor.execute(query, [pftid])

# Fetch a single row using fetchone() method.
data = cursor.fetchall()
#print("Connection established to: ",data)


print(json.dumps(data))

#Closing the connection
conn.close()

#import pymysql

#connection = pymysql.connect(
 #   host='localhost',
  #  port=6543,
   # db="bety"
    #user='bety',
    #password='bety',
    # max_allowed_packet=16777216,
    # connect_timeout=1000,
    # cursorclass=pymysql.cursors.DictCursor
#)
# cursor = connection.cursor()

# query = "select * from pfts_species limit 10"
# try:
#     cursor.execute(query)
# except pymysql.Error as e:
#     print(e)
# results = cursor.fetchall()

# for row in results:
# 	print(row)

# cursor.close()
#connection.close()
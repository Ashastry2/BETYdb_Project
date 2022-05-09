#!/usr/bin/env python3

import cgi
import psycopg2
from string import Template 
import cgitb
cgitb.enable()
import json

def flatten(t):
    return [item for sublist in t for item in sublist]

def executeQuery(query, params):
  connection =psycopg2.connect(
   database="bety", user='postgres', password='', host='127.0.0.1', port= '6543'
)
  cursor = connection.cursor()
  try:
      cursor.execute(query,params)
  except psycopg2.Error as e:
      print(e)
  results = cursor.fetchall()
  connection.commit()
  return(results)

form = cgi.FieldStorage() 

if (form):
    query =  form.getvalue("query","")
    if (query == "species"):
        s = form.getvalue("q", "")

        #cursor.execute('SELECT * FROM goats WHERE name LIKE %(name)s', { 'name': '%{}%'.format(name)})
        term= s.replace('=', '==').replace('%', '=%').replace('_', '=_')
        sql= "select scientificname from species where scientificname ILIKE %(like)s"
        sitesResults =  executeQuery(sql, dict(like= term+'%'))

        sitesResultsFlat = []
        for row in sitesResults:
          sitesResultsFlat += [row[0]]

        #speciesNamesquery = """select scientificname from species where scientificname like '%(name)s'"""
        #sitesResults = executeQuery(speciesNamesquery, { 'name': '%{}%'.format(s)})
        #print(sitesResults)
        return(json.dumps(sitesResultsFlat))
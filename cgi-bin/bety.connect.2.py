#!/usr/bin/env python3

import cgi
import psycopg2
from string import Template 
import cgitb
cgitb.enable()
import json

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


#retrieve input data from the web server
form = cgi.FieldStorage() 

print("Content-type: text/html\n")

def map_label(city, state, country):
  label = ""
  if city != "":
    label += city
    label += ", "
  if state != "":
    label += state
    label += ", "
  if country != "":
    label += country
  return(label)

if (form):
    query =  form.getvalue("query","")
    if (query == "site_detail"):
        id = form.getvalue("id", "")
        siteDetailCountQuery = """select count(*) from traits t
        join species s on (t.specie_id = s.id)
        join treatments t2 on (t2.id = t.treatment_id)
        join variables v on (v.id = t.variable_id)
        where t.site_id  = %(id)s"""

        siteDetailCountResults =  executeQuery(siteDetailCountQuery, dict(id= id))
        #print(siteDetailCountResults[0][0])

        if (siteDetailCountResults[0][0] == 0):
          print(json.dumps({
          'error': 1
          }))
        else :
          siteDetailQuery = """select  s.scientificname , t2."name" , v."name",  t.mean , t.n  from traits t
            join species s on (t.specie_id = s.id)
            join treatments t2 on (t2.id = t.treatment_id)
            join variables v on (v.id = t.variable_id)
            where t.site_id  = %(id)s"""
          siteDetailResults =  executeQuery(siteDetailQuery, dict(id= id))
          plot_data = [[ 'Species Name', 'Trait Name', 'Variable Name', 'Mean', 'n']]
          for row in siteDetailResults:
            plot_data.append([ row[0], row[1], row[2], row[3], row[4]])
          print(json.dumps({
            'error': 0,
            'plot_data':plot_data
            }))
    if (query == "species"):
        s = form.getvalue("q", "")

        #cursor.execute('SELECT * FROM goats WHERE name LIKE %(name)s', { 'name': '%{}%'.format(name)})
        term= s.replace('=', '==').replace('%', '=%').replace('_', '=_')
        sql= "select scientificname from species where scientificname ILIKE %(like)s"
        sitesResults =  executeQuery(sql, dict(like= term+'%'))

        sitesResultsFlat = []
        for row in sitesResults:
          sitesResultsFlat += [row[0]]
        print(json.dumps(sitesResultsFlat))
    if (query == "sites_yield"):
        sitesYieldQuery = """select latitude , longitude , city, state, country , cultivars_name , scientificname , sum(mean * n) as overall_mean, site_id  from 
        (
        SELECT sites.id as site_id, st_y(geometry) as latitude, st_x(geometry) as longitude,city, state, country , mean, coalesce(n, 1) as n, cultivars.name as cultivars_name, species.scientificname 
        FROM sites join yields on (yields.site_id = sites.id) 
        join cultivars on (yields.cultivar_id = cultivars.id)
        join species on (yields.specie_id = species.id)
        WHERE st_geometrytype(geometry) = 'ST_Point' and mean is not null ) as t
        group by latitude, longitude, city, state, country , cultivars_name , scientificname , site_id
        limit 100
        """
        sitesResults = executeQuery(sitesYieldQuery, [])
        plot_data = [[ 'id', 'Latitude', 'Longitude', 'Site Name',  "Cultivars", "Scientific Name", 'Mean Yield']]
        for row in sitesResults:
          #print(row)
          row_label = map_label(row[2], row[3], row[4])
          plot_data.append([ row[8], row[0], row[1], row_label, row[5], row[6], row[7]])
        print(json.dumps({
          'error': 0,
          'plot_data':plot_data
          }))
    if (query == "sites"):
        #print(query)
        sitesQuery = """SELECT st_y(geometry) as latitude, st_x(geometry) as longitude, city, state, country , map, mat, id FROM sites WHERE st_geometrytype(geometry) = 'ST_Point'  and map is not null and mat is not null limit 100"""

        sitesResults = executeQuery(sitesQuery, [])
        #plot_data = [['Latitude', 'Longitude', 'Label', 'MAP', 'MAT']]
        plot_data = [[ 'id', 'Latitude', 'Longitude', 'Site Name', 'MAP', 'MAT']]
        for row in sitesResults:
          #print(row)
          row_label = map_label(row[2], row[3], row[4])
          map = row[5]
          mat = row[6]
          if map is not None:
            map = float(map)
          if mat is not None:
            mat = float(mat)
          #plot_data.append([row[0], row[1], map, mat, row_label])
          plot_data.append([row[7], row[0], row[1], row_label, map, mat])
        print(json.dumps({
          'error': 0,
          'plot_data':plot_data
          }))
 

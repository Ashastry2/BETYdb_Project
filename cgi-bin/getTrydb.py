#!/usr/bin/env python3

import cgi 
import io
import cgitb
cgitb.enable()
import sys
import psycopg2
import json
import pandas as pd
import numpy as np
# Make a function to execute query 

def execute_query(query,s,t):
    connection = psycopg2.connect(
        host='127.0.0.1',
        user='postgres',
        password='',
        database='bety',
        port=6543)
    cursor = connection.cursor()
    
    try:
        if(s == ""):
          cursor.execute(query) 
        else:
          if(t == ""):
            cursor.execute(query,[s])
          if(t != ""):
            cursor.execute(query,[s,t])
    except psycopg2.Error as e:
        print(e)
    results = cursor.fetchall()
    connection.commit()
    return(results)


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def execute_query2(query,s,t):
    connection = psycopg2.connect(
        host='127.0.0.1',
        user='postgres',
        password='',
        database='bety',
        port=6543)
    cursor = connection.cursor()
    
    try:
       if(s == ""):
         cursor.execute(query)
       else:
          if(t == ""):
            cursor.execute(query,[s])
          if(t != ""):
            cursor.execute(query,[s,t])
    except psycopg2.Error as e:
        print(e)
    results = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    connection.commit()
    #results = np.vstack([results,colnames])
    return(colnames + results)


#form = cgi.FieldStorage()

#print("Content-type: text/html\n")

# Original form 

html_template = """
        <html>
           <head>
           </head>
            <body>
            <style>
            .header{
             padding:2px;
             text-align:center;
             background:#5ba3eb;
             color:white;            
             }
            
            .navigation{
             display: block;
	     text-align:center;
             background:#edf1f5;
             color:black;
             text-decoration:none;
             overflow: hidden;
            
             }

            @keyframes slide {
            0%   {background-color: yellow; left:-200px; top:0px;}
            100% { background-color: #5ba3eb; left:200px; top:0px;}
            }

            .textbut {
             border: black;
             font-size: 20px;
             padding: 10px 10px 10px 10px; 
             background-color: YellowChiffon;
             text-align: center;
             position: relative;
             animation-name: slide;
             animation-duration: 4s;
             animation-iteration-count: infinite;
             animation-direction: alternate;
             }
           
             .page {
             text-align: center; 
             }

            </style>
            <title>BETYdb Biofuel Ecophysiological Traits and Yields Database</title>
              <div class="header">
                 <h1>Welcome to BETYdb</h1>
              </div>
              <div class="navigation">
                <a href= "https://www.betydb.org">BETYdb</a>
                <a href= "https://www.try-db.org/TryWeb/Home.php">TRYdb</a>
              </div>

                 <p>This interface will provide an updated traits information for species from TRY database. Trait information from TRY database gets updated regularly. In order to provide the updated trait information from TRYdb in the form of BETYdb, we have developed this interface. You can query information pertaining to a certain species or trait. We acquire the data from the TRY database, modify the data to fit the schema for BETYdb and connect the information between the two databases. Visualization options are available through this interface</p>
          </head>
          <body>
          <div class = "page"> 
          <h2>Please enter species name or Traits</h2> <button class = "textbut">Recent merge from TRY added 1000 new traits</button>          
          <form name = "getTrydb" action = "https://bioed.bu.edu/cgi-bin/students_22/Group_N/getTrydb.py" METHOD="GET">
             Species<input type = "text" name = "Species" text-align = "center" placeholder="Abronia umbellata"><br>
	     Traits<input type = "text" name = "Traits" placeholder="stomatal_conductance"><br>
            <input type = "submit" value = "Submit" />
            <h4> Click submit to see the information about the species/trait</h4>
        </div> 
        </body>
         </form>
"""

form = cgi.FieldStorage()

#query = "select * from species"
#results = execute_query(query,"hi")
print("Content-type: text/html\n")



if (form):
     #print("Content-type: text/html\n")
    # print(html_template)

     Species = form.getvalue('species','')
     Selector = form.getvalue('selector','')
     Traits  = form.getvalue('traits','')
     pfts = form.getvalue('pfts','')
   
     if(Selector == "species"):
       new = '' + Species+ '%'+ ''
       query = "select concat(species,' ',genus) as species from species where species like %s limit 10"
       results = execute_query(query,new,t ="")
       flattenresults = []
       for row in results:
          flattenresults += [row[0]]
       print(json.dumps(flattenresults))

     if(Selector == "findtraits"):
       query = "select distinct name from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where species = %s and genus = %s"
       breaks = Species.split()
       new = '' + breaks[0]+ ''
       new2 = ''+ breaks[1]+ ''
       results = execute_query(query,new, new2)
       flattenresults = []
       for row in results:
          flattenresults += [row[0]]
       print(json.dumps(results))

     if(Selector == "traits"):
        query = "select distinct name from traits join variables on (traits.variable_id  = variables.id) where name like %s"
        new = '' + '%' + Traits + '%' + ''
        results = execute_query(query,new, t = "")
        flattenresults = []
        for row in results:
           flattenresults += [row[0]]
        print(json.dumps(flattenresults))

     if(Selector == "findspecies"):
       query = "select distinct concat(species,' ',genus) as species from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where name = %s"
       new = '' + Traits+ ''
       results = execute_query(query,new,t = "")
       flattenresults = []
       for row in results:
          flattenresults += [row[0]]
       print(json.dumps(results))

     if(Selector == "makehist"):
       query ="select name, mean  from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where species = %s and genus = %s"
       breaks = Species.split()
       new = '' + breaks[0] + ''
       new2 = '' + breaks[1]+ ''
       results = execute_query(query,new,new2)
#       print(json.dumps(results))
       resultsDict = {}
       for result in results:
        if result[0] in resultsDict:
          resultsDict[result[0]].append(result[1])
        else:
          resultsDict[result[0]] = [result[1]]
       resultsFinal = []
       #Col 1: Number specifying the low/minimum value of this marker. This is the base of the candle's center line. The column label is used as the series label in the legend (while the labels of the other columns are ignored).
        #Col 2: Number specifying the opening/initial value of this marker. This is one vertical border of the candle. If less than the column 3 value, the candle will be filled; otherwise it will be hollow.
        #Col 3: Number specifying the closing/final value of this marker. This is the second vertical border of the candle. If less than the column 2 value, the candle will be hollow; otherwise it will be filled.
        #Col 4: Number specifying the high/maximum value of this marker. This is the top of the candle's center line.    
       for result in resultsDict:
          vals = resultsDict[result]
          q75, q25 = np.percentile(vals, [75 ,25])
          resultsFinal += [[result] + [min(vals)] + [q25] + [q75] + [max(vals)]]
       print(json.dumps(resultsFinal))







     if(Selector == "makehist2"):
       query ="select concat(species,' ', genus) as species, mean  from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where name = %s"
       new = '' + Traits + ''
       results = execute_query(query,new, t = "")
   #    print(json.dumps(results))
       resultsDict = {}
       for result in results:
        if result[0] in resultsDict:
          resultsDict[result[0]].append(result[1])
        else:
          resultsDict[result[0]] = [result[1]]
       resultsFinal = []
       for result in resultsDict:
          vals = resultsDict[result]
          q75, q25 = np.percentile(vals, [75 ,25])
          resultsFinal += [[result] + [min(vals)] + [q25] + [q75] + [max(vals)]]
       print(json.dumps(resultsFinal))


 

     if(Selector == "download"):
       query ="select * from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where species = %s and genus = %s"
       breaks = Species.split()
       new = '' + breaks[0]+ ''
       new2 = ''+ breaks[1]+ ''
       results = execute_query2(query,new, new2)
      # A = np.vstack([results,A])
       print(json.dumps(results,default=str))


     if(Selector == "download2"):
       query ="select distinct * from species join traits on (species.id = specie_id) join variables on (traits.variable_id  = variables.id) where name = %s"
       new = '' + Traits + ''
       results = execute_query2(query,new, t="")
       print(json.dumps(results,default=str))



     if(Selector == "pfts"):
       name = '/var/www/html/students_22/Group_N/PFTdataExplore/'
       full = name + pfts + '.txt'
       data = pd.read_csv(full,sep ="\t", encoding='latin-1',header = None) 
       data = data.head(20)
       array = data.to_numpy()
       print(json.dumps(array.tolist()))
      # print(json.dumps(json.loads(data.to_json(orient='index')), indent=2))









#     if(Species != ""):
 #        if(Traits == ""):

#            query = "select genus,species from species where species = %s"
 #           results = execute_query(query, Species, "")
 #           print("Content-type: text/html\n")
 #           print(json.dumps(results))
                
 #        else:
  #          query = "select genus,species from species join traits on species.id = specie_id join variables on traits.variable_id  = variables.id  where species = %s and Description = %s"
   #         results = execute_query(query,Species,Traits)
    #        print("Content-type: text/html\n")
     #       print(html_template)
            
   #  elif(Species == ""):
    #       if(Traits == ""):
     #          print("Content-type: text/html\n")
      #         print("Please enter either species or traits name") 
       #    else:
      #         query = "select species from species join traits on species.id = specie_id join variables on traits.variable_id  = variables.id where Name = %s"
      #         print("Content-type: text/html\n")
    #           results = execute_query(query, "", Traits)
     #          print(json.dumps(results))
 
    #}
    # for row in results:
     #    plot_data.append([row[0],row[1]])
     


#else:
 #   print("Content-type: text/html\n")
#    print(html_template)

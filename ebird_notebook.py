# Importing ebird.api and its respective module to get recorded bird observations 
import ebird.api
import os
import re 
from ebird.api import get_observations
arcpy.env.overwriteOutput = True

# getting ebird records from utah in the last week

# "api-token" is api token code given from ebird website. You must create an ebird acount to get one  'US-UT' filters obvservations to utah, back=30 is the observation from last 30 days) 
records = get_observations("api-token", 'US-UT', back=30)


# Creating empty lists that will be populated with info from records variable 

com_name = []
sci_name = []
loc_name = []
date = []
lat = []
long = [] 
allaboutbird = []
ebirdlink = []

# For loop itteriates through records variable and appends data to lists created above

for record in records:
    com_name.append(record["comName"])
    sci_name.append(record["sciName"])
    loc_name.append(record['locName'])
    date.append(record['obsDt'])
    lat.append(record['lat'])
    long.append(record['lng'])
    allaboutbird.append(record['comName'])
    ebirdlink.append(record['speciesCode'])

# Creating feature class and field attributes that will be populated with data

# set outpath to location of the current project
outPath = arcpy.env.workspace = os.path.dirname(sys.argv[0])

outName = "bird_pts"
geometry_type = "POINT"


spatial_reference = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],\
              PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],\
              VERTCS['WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],\
              PARAMETER['Vertical_Shift',0.0],PARAMETER['Direction',1.0],UNIT['Meter',1.0]];\
              -400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;\
              0.001;0.001;IsHighPrecision"

sr = arcpy.SpatialReference(text= spatial_reference)
arcpy.CreateFeatureclass_management(outPath, outName,geometry_type,spatial_reference = sr)
arcpy.management.AddField("bird_pts", field_name = "com_name", field_type = "TEXT")
arcpy.management.AddField("bird_pts", field_name = "sci_name", field_type = "TEXT")
arcpy.management.AddField("bird_pts", field_name = "loc_name", field_type = "TEXT")
arcpy.management.AddField("bird_pts", field_name = "obsDt", field_type = "DATE")
arcpy.management.AddField("bird_pts", field_name = "LATITUDE", field_type = "FLOAT")
arcpy.management.AddField("bird_pts", field_name = "LONGITUDE", field_type = "FLOAT")
arcpy.management.AddField("bird_pts", field_name = "ABOUTBIRD", field_type = "TEXT")
arcpy.management.AddField("bird_pts", field_name = "EBIRD", field_type = "TEXT")




# Useing re module to subsitute unwanted charecters for a weblink to allaboutbirds.org
sub_all = [re.sub("'", '', s) for s in allaboutbird]
sub_all = [re.sub(" ", '_', s) for s in sub_all]

weblink = []
for i in sub_all:
    weblink.append("https://www.allaboutbirds.org/guide/" + i)
birdlink = []
for i in ebirdlink:
    birdlink.append("https://ebird.org/species/" + i)
    
# inserting data using insertCursor     
field_info = zip(com_name,sci_name,loc_name,date,lat,long,weblink,birdlink)

with arcpy.da.InsertCursor("bird_pts",("com_name","sci_name","loc_name","obsDT","LATITUDE","LONGITUDE","ABOUTBIRD",'EBIRD')) as cursor:
    for row in field_info:
        row = row[0:8]
        cursor.insertRow(row)
    del cursor 
    
 # Make the XY event layer...
arcpy.management.XYTableToPoint("bird_pts", "bird_points",
                                "LONGITUDE", "LATITUDE")

# Deletes original bird_pts layer from TOC 
arcpy.management.Delete("bird_pts")

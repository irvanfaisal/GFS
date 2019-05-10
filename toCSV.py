import netCDF4
import urllib3
from bs4 import BeautifulSoup
import csv

workPath = 'pathToData'

# Get Latest GFS Data Information

url = 'http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p25deg/latest.html'
http = urllib3.PoolManager() 
response = http.request('GET',url)
soup = BeautifulSoup(response.data.decode('utf-8'),'html.parser')
filename = soup.body.find('a').text

# Define Parameters to Download

parameters = '\
Temperature_height_above_ground,\
Apparent_temperature_height_above_ground,\
Maximum_temperature_height_above_ground_Mixed_intervals_Maximum,\
Minimum_temperature_height_above_ground_Mixed_intervals_Minimum,\
u-component_of_wind_height_above_ground,\
v-component_of_wind_height_above_ground,\
Relative_humidity_height_above_ground,\
Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average,\
Total_precipitation_surface_Mixed_intervals_Accumulation\
'

# define Bounding Box

boundNorth = 6
boundWest = 90
boundEast = 141
boundSouth = -11

dataName = 'GFS.nc'

downloadURL = "http://thredds.ucar.edu/thredds/ncss/grib/NCEP/GFS/Global_0p25deg/" + filename + "?var=" + parameters + "&north=" + str(boundNorth) + "&west=" + str(boundWest) + "&east=" + str(boundEast) + "&south=" + str(boundSouth) + "&temporal=all"

# Download Data

r = http.request('GET', downloadURL, preload_content=False)
with open(workPath + '/' + dataName, 'wb') as out:
    while True:
        data = r.read(2048)
        if not data:
            break
        out.write(data)
r.release_conn()

# Load Data

dataPath = workPath + '/' + dataName
nc = netCDF4.Dataset(dataPath,mode='r')

# Get Parameters to be Extracted

lat = nc.variables['lat']
lon = nc.variables['lon']
try:
    time_var = nc.variables['time']
except:
    try:
        time_var = nc.variables['time1']
    except:
        time_var = nc.variables['time2']
        pass
dtime = netCDF4.num2date(time_var[:],time_var.units)
temp = nc.variables['Temperature_height_above_ground']
atemp = nc.variables['Apparent_temperature_height_above_ground']
max = nc.variables['Maximum_temperature_height_above_ground_Mixed_intervals_Maximum']
min = nc.variables['Minimum_temperature_height_above_ground_Mixed_intervals_Minimum']
u = nc.variables['u-component_of_wind_height_above_ground']
v = nc.variables['v-component_of_wind_height_above_ground']
rh = nc.variables['Relative_humidity_height_above_ground']
cloud = nc.variables['Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average']
rain = nc.variables['Total_precipitation_surface_Mixed_intervals_Accumulation']

# Slice data from 003 to 385 forecast hour to make it uniform length for all parameters

time = dtime[0:55]
dataTemp = temp[1:56,0,:,:]
dataAtemp = atemp[1:56,0,:,:]
dataMax = max[0:55,0,:,:]
dataMin = min[0:55,0,:,:]
dataUwind = u[1:56,0,:,:]
dataVwind = v[1:56,0,:,:]
dataRh = rh[1:56,0,:,:]
dataCloud = cloud[0:55,:,:]
dataRain = rain[0:55,:,:]

# Write a CSV File

csvName = 'data.csv'
csvHeader = [
'forecast',
'datetime',
'lon',
'lat',
'temperature',
'apparent_temperature',
'maximum_temperature',
'minimum_temperature',
'u_wind',
'v_wind',
'humidity',
'cloud',
'precipitation'
]
with open(workPath + '/latest.txt', 'w') as filehandle:  
    filehandle.write(filename[19:32])
	
with open(workPath + '/' + csvName, 'w', newline="") as csvFile:
	writer = csv.writer(csvFile,delimiter=",")
	writer.writerow([g for g in csvHeader]) 
	for i, t in enumerate(time):
		for j, y in enumerate(lat):
			for k, x in enumerate(lon):
				row = [filename[19:32],t,x,y,dataTemp[i,j,k],dataAtemp[i,j,k],dataMax[i,j,k],dataMin[i,j,k],dataUwind[i,j,k],dataVwind[i,j,k],dataRh[i,j,k],dataCloud[i,j,k],dataRain[i,j,k]]		
				writer.writerow(row)

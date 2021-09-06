import gdal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from osgeo.osr import CoordinateTransformation, SpatialReference
from math import pi
from pyproj import Transformer, Proj, CRS


# 1. Завантажити растрові геодані в програмне середовище Python.
filename = "tif/ASTGTMV003_N37W118_num.tif"
dataset = gdal.Open(filename)

# 2. Здійснити в середовищі Python перепроектування завантажених
# растрових геоданих із поточної системи координат у систему UTM WGS84
# із вибором відповідної зони.

proj = SpatialReference(dataset.GetProjection())  #Просторова прив'язка із завантаженого файла за координатами tif file
# 3. Сформувати (отримавши відповідні значення Value)
# та експортувати з середовища Python у табличному/текстовому форматі наступну таблицю:

band = dataset.GetRasterBand(1)  #отримуємо окремий канал із растру
bandArray = band.ReadAsArray()  #отриманий канал переводимо в масив

# 1
dataType = gdal.GetDataTypeName(band.DataType)  #отримуємо тип даних нашого масиву з каналом растру (byte), значення від 0 до 255

# 2
noData = band.GetNoDataValue()
print(noData)  #перевірка даних цілісності даних у отриманому масиві каналу

# 3
minVal = np.min(bandArray)
maxVal = np.max(bandArray)
meanVal = np.mean(bandArray)
stdVal = np.std(bandArray)
print(minVal, maxVal, meanVal, stdVal)

# 4
epsg = proj.GetAttrValue('AUTHORITY', 1)  #система координат використана в при геозйомці WGS 84 -- WGS84 - World Geodetic System 1984, used in GPS
# 5
'''''''''
Отримуємо 
X координата лівого верхнього пікселя
ширина пікселя
обертання
Y координата лівого верхнього пікселя
обертання
висота пікселя
'''''''''
gt = dataset.GetGeoTransform()

#отримуємо розмір растра в пікселях
cols, rows = dataset.RasterXSize, dataset.RasterYSize

#отримуємо координати території
LatitudeX = gt[3] + cols * gt[4] + rows * gt[5]
LongitudeX = gt[0]
LatitudeY = gt[3]
LongitudeY = gt[0] + cols * gt[1] + rows * gt[2]

pixelSize = [gt[1], gt[5]]  #роззмір пікселя на файлі tif в градусах

# 4. Здійснити задану операцію трансформації растрових геоданих

file = "tif/ASTGTMV003_N37W118_dem.tif"
demData = gdal.Open(file)
demDataArr = demData.ReadAsArray()

proj = SpatialReference(wkt=dataset.GetProjection()) #задаємо проекцію із завантаженого файлу у створюваний

binary = np.where(demDataArr > 2500, 1, 0) #масив висот де висота більше 2500
plt.figure()
plt.imshow(binary)
plt.show()

proj = SpatialReference(wkt=dataset.GetProjection())  #Просторова прив'язка із завантаженого файла за координатами tif file

colsDem, rowsDem = demData.RasterXSize, demData.RasterYSize
bands = 1
geoT = demData.GetGeoTransform()
proj = demData.GetProjection()

pixels = np.count_nonzero(binary == 1)
transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
transformated_PixelSize_m = transformer.transform(gt[1], gt[5])
OnePixelArea_m = abs(transfo08rmated_PixelSize_m[0] * transformated_PixelSize_m[1])
total_RasterArea_m = (cols**2)*OnePixelArea_m
total_ExpRasterArea_m = pixels*OnePixelArea_m




OnePixel = abs(geoT[1] * geoT[5])
area_Pixels = pixels * OnePixel  #площа території яка вища за 2500 в градусах
area_OneDegree = ((2*pi*6371000)/360)**2  #площа 1 градусу в км2 на сфері
total_RasterArea = ((cols**2) * OnePixel) * area_OneDegree  #площа досліджуваної території
total_ResArea = area_Pixels*area_OneDegree  #площа території де висоти більше 2500 в км2


# Експортувати отриманий результат у форматі, придатному для перегляду та подальшої обробки в середовищі ГІС.

driver = gdal.GetDriverByName('GTiff')  #підготовка класу файлу для подальшої роботи
driver.Register()

outds = driver.Create("tif/bin.tif", colsDem, rowsDem, bands, gdal.GDT_Byte)

#метадата для створеного файла tif

outds.SetGeoTransform(geoT)
outds.SetProjection(proj)

outband = outds.GetRasterBand(1)  #створення каналу в растр файлі
outband.WriteArray(binary)

# Make table

stat = pd.DataFrame({'Spec': 'Value',
                     'DataType': [dataType],
                     'NoData': [noData],
                     'Min': [minVal],
                     'Max': [maxVal],
                     'Mean': [meanVal],
                     'Std': [stdVal],
                     'EPSG': [epsg],
                     'LatitudeX': [LatitudeX],
                     'LongitudeX': [LongitudeX],
                     'LatitudeY': [LatitudeY],
                     'LongitudeY': [LongitudeY],
                     'Rows': [rows],
                     'Columns': [cols],
                     'Pixel Size': [pixelSize],
                     "area_Pixels": [area_Pixels],
                     "area_OneDegree": [area_OneDegree],
                     "total_RasterArea": [total_RasterArea],
                     "total_ResArea": [total_ResArea],
                     'transformated_PixelSize_m': [transformated_PixelSize_m],
                     'OnePixelArea_m': [OnePixelArea_m],
                     'total_RasterArea_m': [total_RasterArea_m],
                     'total_ExpRasterArea_m': [total_ExpRasterArea_m]
                     })



def difference_area(area1, area2):
    diff = area1 - area2
    return print(f"First method result: {area1/1000} km2\n"
                 f"Second method result: {area2/1000} km2\n"
                 f"Difference between method 1 and method 2: {diff/1000} km2")


difference_area(total_RasterArea, total_RasterArea_m)

print(stat.transpose())
stat.to_csv('table.csv')
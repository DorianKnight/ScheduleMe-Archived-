from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from ScheduleMe import Schedule

fig = plt.figure()
ax = plt.axes(projection='3d')

Calendar = Schedule()
rawData = Calendar.graphFormat
print(Calendar.graphFormat)
print("Correlation coefficient",Calendar.correlationCoefficient())

#Isolate the data into arrays for each axis
xTrendData = []
yTrendData = []
zTrendData = []

xUserData = []
yUserData = []
zUserData = []

xMean = []
yMean = []
zMean = []

n = len(rawData)
xCounter = 1

#X axis - event type - discontinuous event
for i in range(n):
    xTrendData.append(xCounter)
    xUserData.append(xCounter)
    xMean.append(xCounter)
    xCounter += 1

#Y axis - start time of event
for item in rawData:
    yTrendData.append(item[0][1])
    yUserData.append(item[1][1])
    yMean.append(Calendar.meanTime)

#Z axis - event duration
for item in rawData:
    zTrendData.append(item[0][2])
    zUserData.append(item[1][2])
    zMean.append(Calendar.meanDuration)

#Plot the data
ax.plot3D(xTrendData,yTrendData,zTrendData, 'blue')
ax.plot3D(xMean,yMean,zMean, 'red')
ax.scatter3D(xUserData, yUserData, zUserData)

plt.show()

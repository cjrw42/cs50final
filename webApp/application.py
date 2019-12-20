from flask import Flask, Markup, jsonify, redirect, render_template, request
from datetime import datetime
import functions


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



#===========================
# index
#===========================

@app.route('/')
def index():
    return render_template("index.html")
    





#===========================
# sys
#===========================

@app.route('/sys')
def sys():
    
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    
    

        
    # Case temps - 24 hours
    query = "select timestamp,encTemp from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    data1 = functions.lOfTuplesToLoL(rows)
    for i in range (len(data1)):
        data1[i][0] = functions.epochToTime(data1[i][0])


    # CPU temps - 24 hours
    query = "select timestamp,cpuTemp from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    data2 = functions.lOfTuplesToLoL(rows)
    for i in range (len(data2)):
        data2[i][0] = functions.epochToTime(data2[i][0])


    # load avs - 24 hours
    query = "select timestamp,loadAv from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    data3 = functions.lOfTuplesToLoL(rows)
    for i in range (len(data3)):
        data3[i][0] = functions.epochToTime(data3[i][0])
        
        
    # mem free - all time
    query = "select timestamp,memFree from sensordata where id % 288 = 0"
    rows = functions.dbGetRows(query)
    data4 = functions.lOfTuplesToLoL(rows)
    for i in range (len(data4)):
        data4[i][0] = functions.epochToDateTime(data4[i][0])
        
        

    lastDataPoints = functions.getLastRow()
    uptime = round((lastDataPoints[11]/60)/60)

    return render_template("sys.html", data1 = data1, data2 = data2, data3 = data3, data4 = data4, uptime = uptime,)
    





#===========================
# light
#===========================


@app.route('/day/li')
def dayLi():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,light from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [light]", graphTitle = "light", data=data)


@app.route('/week/li')
def weekLi():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,light from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [light]", graphTitle = "light", data=data)



@app.route('/month/li')
def monthLi():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,light from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [light]", graphTitle = "light", data=data)




#===========================
# rain
#===========================

@app.route('/day/rd')
def dayRd():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,rain from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [Rain/Dew]", graphTitle = "Rain/Dew", data=data)


@app.route('/week/rd')
def weekRd():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,rain from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [Rain/Dew]", graphTitle = "Rain/Dew", data=data)



@app.route('/month/rd')
def monthRd():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,rain from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [Rain/Dew]", graphTitle = "Rain/Dew", data=data)




#===========================
# soil
#===========================

@app.route('/day/sm')
def daySm():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,soil from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [Soil Moisture]", graphTitle = "Soil Moisture", data=data)


@app.route('/week/sm')
def weekSm():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,soil from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [Soil Moisture]", graphTitle = "Soil Moisture", data=data)



@app.route('/month/sm')
def monthSm():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,soil from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [Soil Moisture]", graphTitle = "Soil Moisture", data=data)





#===========================
# pressure
#===========================

@app.route('/day/pr')
def dayPr():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,pressure from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [Pressure]", graphTitle = "Pressure (mbar)", data=data)


@app.route('/week/pr')
def weekPr():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,pressure from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [Pressure]", graphTitle = "Pressure (mbar)", data=data)



@app.route('/month/pr')
def monthPr():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,pressure from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [Pressure]", graphTitle = "Pressure (mbar)", data=data)






#===========================
# humidity
#===========================

@app.route('/day/hg')
def dayHg():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,humidity from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [Humidity]", graphTitle = "Humidity (%)", data=data)


@app.route('/week/hg')
def weekHg():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,humidity from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [Humidity]", graphTitle = "Humidity (%)", data=data)



@app.route('/month/hg')
def monthHg():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,humidity from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [Humidity]", graphTitle = "Humidity (%)", data=data)






#===========================
# temperature
#===========================

@app.route('/day/tc')
def dayTc():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aDayAgo = now - 84000
    query = "select timestamp,temperature from sensordata where timestamp >= " + str(aDayAgo) 
    rows = functions.dbGetRows(query)
    
    # convert those perky immutable tuples in to a list of lists so we can 
    # change the epoch into whatever label value makes most sense
    data = functions.lOfTuplesToLoL(rows)

    # now convert the epochtime to something more readable
    for i in range (len(data)):
        data[i][0] = functions.epochToTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 24 Hours [Temperature]", graphTitle = "Temperature (Centigrade)", data=data)


@app.route('/week/tc')
def weekTc():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aWeekAgo = now - (84000*7)
    # limt the query to once aevery half hour data points using  modulo 6 on the id field
    query = "select timestamp,temperature from sensordata where timestamp >= " + str(aWeekAgo) + " and id % 6 = 0" 
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDayTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last Week (0.5 hourly samples) [Temperature]", graphTitle = "Temperature (Centigrade)", data=data)



@app.route('/month/tc')
def monthTc():
    
    # work out the timestamp range we need
    
    now = functions.myTimeStamp()
    aMonthAgo = now - (84000*28)
    
    # limt the query to once an hour data points using  modulo 12 on the id field
    query = "select timestamp,temperature from sensordata where timestamp >= " + str(aMonthAgo) + " and id % 12 = 0" 
    
    rows = functions.dbGetRows(query)
    data = functions.lOfTuplesToLoL(rows)
    for i in range (len(data)):
        data[i][0] = functions.epochToDateTime(data[i][0])

    return render_template('dataGraph.html', heading = "Sensor Data :: Last 28 Days (hourly samples) [Temperature]", graphTitle = "Temperature (Centigrade)", data=data)




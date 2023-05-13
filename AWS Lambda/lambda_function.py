import json
import urllib.request
import mysql.connector
import sys
import time
import os


def lambda_handler(event, context):
    conn = None

    try:
        conn = mysql.connector.connect(
            HOST = os.getenv('DB_HOST')
            USERNAME = os.environ.get('DB_USERNAME')
            PASSWORD = os.environ.get('DB_PASSWORD')
            DBNAME = os.environ.get('DB_NAME')
            
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            port=3306,
            database=DBNAME
        )

    except mysql.connector.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    try:
        API = os.environ.get('API_KEY')
        url = "https://api.nationaltransport.ie/gtfsr/v2/gtfsr?format=json"

        hdr = {
            # Request headers
            'Cache-Control': 'no-cache',
            'x-api-key': API,
        }

        req = urllib.request.Request(url, headers=hdr)
        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)

        # print(response.getcode())
        data = json.loads(response.read())
        # print(data)

        if not data:
            raise Exception('Failed to read data')

    except Exception as e:
        print(e)
        sys.exit(1)

    cursor = conn.cursor()
    startExecute1 = time.time()
    cursor.execute("""drop table if exists realtime_trip_update_bak""")
    print(f"1: {time.time() - startExecute1}")
    cursor.execute("""drop table if exists realtime_stop_time_update_bak""")
    print(f"2: {time.time() - startExecute1}")

    saveDataQuery = """create table realtime_trip_update_bak select * from realtime_trip_update;"""
    updateSaveDataQuery = """create table realtime_stop_time_update_bak select * from realtime_stop_time_update;"""
    cursor.execute(saveDataQuery)
    cursor.execute(updateSaveDataQuery)

    cursor.execute("""truncate table realtime_trip_update""")
    print(f"3: {time.time() - startExecute1}")
    cursor.execute("""truncate table realtime_stop_time_update""")
    print(f"4: {time.time() - startExecute1}")
    tripUpdateQuery = """INSERT INTO realtime_trip_update (id, trip_id, route_id, start_time, start_date, schedule_relationship, direction_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    stopTimeUpdateQuery = """INSERT INTO realtime_stop_time_update (trip_update_id, stop_sequence, stop_id, arrival_delay, arrival_time, arrival_uncertainty, departure_delay, departure_time, departure_uncertainty, schedule_relationship) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    for entity in data['entity']:
        tripUpdate = entity.get('trip_update')
        trip = tripUpdate.get('trip')
        id = entity.get('id')

        cursor.execute(tripUpdateQuery, (id, trip.get('trip_id'), trip.get('route_id'),
                                         trip.get('start_time'), trip.get('start_date'),
                                         trip.get('schedule_relationship'),
                                         trip.get('direction_id')))
        print(f"5: {time.time() - startExecute1}")
        if tripUpdate.get('stop_time_update') is None:
            continue

        for stopTimeUpdate in tripUpdate['stop_time_update']:
            arrival = stopTimeUpdate.get("arrival")
            departure = stopTimeUpdate.get("departure")
            stop_sequence = stopTimeUpdate.get('stop_sequence')
            stop_id = stopTimeUpdate.get('stop_id')
            schedule_relationship = stopTimeUpdate.get('schedule_relationship')
            arrivalDelay = None
            arrivalTime = None
            arrivalUncertainty = None
            departureDelay = None
            departureTime = None
            departureUncertainty = None

            if arrival:
                arrivalDelay = stopTimeUpdate['arrival'].get('delay')
                arrivalTime = stopTimeUpdate['arrival'].get('time')
                arrivalUncertainty = stopTimeUpdate['arrival'].get('uncertainty')

            if departure:
                departureDelay = stopTimeUpdate['departure'].get('delay')
                departureTime = stopTimeUpdate['departure'].get('time')
                departureUncertainty = stopTimeUpdate['departure'].get('uncertainty')

            cursor.execute(stopTimeUpdateQuery, (
                id, stop_sequence, stop_id,
                arrivalDelay, arrivalTime, arrivalUncertainty, departureDelay, departureTime,
                departureUncertainty, schedule_relationship))
            print(f"6: {time.time() - startExecute1}")

    conn.commit()
    print(f"7: {time.time() - startExecute1}")

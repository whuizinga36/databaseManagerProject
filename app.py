# misc libraries
import random

# problem child
import mysql.connector, sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, session

# email libraries
import ssl
import smtplib

# import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# calendar libraries
from ics import Calendar, Event

# sql libraries
from mysql.connector import errorcode

# connect to server, print connection status to terminal
try:
    print("Attempting to connect")
    connection = mysql.connector.connect(user=, password=, host=, port=, database=, ssl_ca=, ssl_disabled=False)
    # connection information has been removed

    print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
    exit()
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
    exit()
  else:
    print(err)
    exit()
else:
  cursor = connection.cursor(dictionary=True)


app = Flask('app')

app.secret_key = "passkey"


def sendMail(filename, type):
    if session.get('username') == None:
        return redirect('/')
    email_sender = 
    email_password = 
    email_reciever = 
    # This information has been removed since it was populated with sensitive information

    if type == 0:
        subject = 'Appointment Update'
        body = 'Here to confirm your appointment and send a calendar reminder.\n'

    em = MIMEMultipart()

    em['From'] = email_sender
    em['To'] = ", ".join(email_recievers)
    em['Subject'] = subject
    em.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
   
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    em.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_recievers, em.as_string())

    return

# fixes strings so that they can be inserted in their current form into sql without causing errors
def fixstring(value):
    if session.get('username') == None:
        return redirect('/')
    result = value

    current = 0
    max = len(result)

    while current < max:
        if result[current] == '\'':
            newResult = result[:current] +"''"+result[(current+1):]
            result = newResult
            current += 1
            max += 1
        current += 1

    while current < max:
        if result[current] == '\"':
            newResult = result[:current] +'""'+result[(current+1):]
            result = newResult
            current += 1
            max += 1
        current += 1

    return result


# login page
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = '"+username+"' AND password = '"+password+"'")
        result = cursor.fetchone()

        if result:
            session['username'] = result['username']
            session['useremail'] = result['userEmail']
            return redirect('/home')
        else:
            flash("Login Failed")

        return render_template('login.html')

    return render_template('login.html')


# home page
    # going to need a lot of work for a potential UI revamp
@app.route('/home', methods=['GET','POST'])
def home():
    if session.get('username') == None:
        return redirect('/')
    if request.method == 'POST':
        inputType = request.form['inputtype']

        # confirm passed inspection
            # probably need to remove this considering that passing inspection is on its own page, although could be useful in the future
        if inputType == "0":
            # stuff for conditional
            id = request.form['id']
            cursor.execute("SELECT * FROM stations WHERE stationID = '"+id+"'")
            station = cursor.fetchone()

            cursor.execute("UPDATE stations SET stage = 0 WHERE stationID = '"+id+"'")

            connection.commit()
            return redirect("/home")

        # control appointments
            # this checks the status of appointments and helps them cycle through the system
        elif inputType == "1":
            appointmentID = request.form['appID']
            cursor.execute("SELECT * FROM appointments WHERE appointmentid = "+str(appointmentID))
            appointment = cursor.fetchone()
            if appointment['status'] == 0:
                # iterate by one to show that the machine has been dropped off
                # select a machine and create the machine and app pair
                machine = request.form['serial']

                if machine != "":

                    # combine these two sql statements at another time
                    cursor.execute("UPDATE appointments SET status = 1 WHERE appointmentid = "+appointmentID)

                    cursor.execute("UPDATE appointments SET machine = '"+ machine +"' WHERE appointmentid = "+appointmentID)



                    cursor.execute("INSERT INTO paired VALUES ("+ appointmentID +",'"+ machine +"')")

                    cursor.execute("UPDATE stations SET stage = 1 WHERE stationID = '"+machine+"'")

                    connection.commit()
                    return redirect("/home")
                else:
                    flash("Please make sure to select a station for drop off")
                    return redirect("/home")

            elif appointment['status'] == 3:
                # delete the appointment to show that the machine has been returned
                # get the machine id move to require inspection
                # create a history entry using relevant information, leaving feedback blank
                appid = appointment['appointmentid']

                cursor.execute("SELECT * FROM paired WHERE appid = "+str(appid))
                paired = cursor.fetchone()

                cursor.execute("SELECT * FROM stations WHERE stationID = '"+paired['machineid']+"'")
                machine = cursor.fetchone()

                cursor.execute("SELECT * FROM appointments WHERE appointmentid = "+str(appid))
                appointment = cursor.fetchone()

                cursor.execute("INSERT INTO pastAppointments VALUES("+ str(appid) +", '"+ machine['stationID'] +"', '"+ appointment['dTime'] +"', '"+ fixstring(appointment['hospitalName']) +"', '')")

                cursor.execute("SELECT COUNT(*) FROM pastAppointments")
                count = cursor.fetchall()

                if count[0]['COUNT(*)'] > 100:
                    cursor.execute("SELECT * FROM pastAppointments WHERE appday = (SELECT MIN(appday) FROM pastAppointments)")
                    thisrow = cursor.fetchone()
                    cursor.execute("DELETE FROM pastAppointments WHERE appday ='"+ thisrow[2] +"'")

                cursor.execute("UPDATE stations SET stage = 2 WHERE stationID = '"+machine['stationID']+"'")

                cursor.execute("DELETE FROM appointments WHERE appointmentid = "+str(appid))
                connection.commit()
                return redirect("/home")



            else:
                # iterate by one to show that the machine has been picked up
                cursor.execute("SELECT status FROM appointments WHERE appointmentid = "+ appointmentID)
                current = cursor.fetchone()
                status = current['status']
                cursor.execute("UPDATE appointments SET status = "+ str((status + 1)) +" WHERE appointmentid = "+appointmentID)
                connection.commit()
                return redirect("/home")

        # broken station handling
            # Simply put, this code kinda sucks. This needs a rewrite of the whole broken machine system at some point
        elif inputType == "2":
            machineid = request.form['id']
            cursor.execute("SELECT * FROM stations WHERE stationID = '"+machineid+"'")
            station = cursor.fetchone()

            if station['stage'] == 6:
                cursor.execute("UPDATE stations SET stage = 4 WHERE stationID = '"+machineid+"'")
            else:
                cursor.execute("UPDATE stations SET stage = 6 WHERE stationID = '"+machineid+"'")

            connection.commit()

            return redirect("/home")

        # delete machines
            # again also kinda useless rn but keeping because it may be useful in the future
        else:
            unitid = request.form['id']

            cursor.execute("DELETE FROM stations WHERE stationID = '"+unitid+"'")
            connection.commit()

            return redirect("/home")

    # stuff for creating the actual page

    cursor.execute("SELECT * FROM users")
    test = cursor.fetchall()

    cursor.execute("SELECT * FROM stations")
    stations = cursor.fetchall()

    cursor.execute("SELECT * FROM appointments ORDER BY dTime ASC")
    appointments = cursor.fetchall()

    cursor.execute("SELECT * FROM stations JOIN paired ON stationID = machineid JOIN appointments ON appid = appointmentid")
    assigneds = cursor.fetchall()

    cursor.execute("SELECT * FROM stations WHERE stage = 0")
    availablestations = cursor.fetchall()

    return render_template('home.html', test = test, stations = stations, appointments=appointments, assigneds=assigneds, availablestations=availablestations)


# create a new appointment
    # reminder for me in the future, always keep this its own page

    # may want to change things, especially whats required and what information is given
    # this will depend on feedback from beta
@app.route('/newappointment', methods=['GET', 'POST'])
def appointment():
    if session.get('username') == None:
        return redirect('/')

    if request.method == 'POST':

        dLoc = request.form['dLoc']

        dLoc = fixstring(dLoc)

        dTime = request.form['dTime']
        dInstructions = request.form['dInstructions']
        dInstructions = fixstring(dInstructions)

        pLoc = request.form['pLoc']
        pLoc = fixstring(pLoc)

        pTime = request.form['pTime']
        if pTime < dTime:
            flash("Please make sure the pick up time is after the drop off time")
            return render_template('appointment.html')

        pInstructions = request.form['pInstructions']
        pInstructions = fixstring(pInstructions)

        hospitalName = request.form['hospitalName']
        hospitalName = fixstring(hospitalName)

        comments = request.form['comments']
        comments = fixstring(comments)

        cursor.execute("SELECT appointmentid FROM appointments")
        ids = cursor.fetchall()

        list_ids = []

        for id in ids:
            list_ids.append(id['appointmentid'])

        # add to compare history for error checking
        thisId = random.randint(0,1000000)
        while str(thisId) in list_ids:
            thisId = random.randint(0,1000000)

        # get all random integers and compare with them

        cursor.execute("INSERT INTO appointments VALUES('" + str(thisId) + "', '" + dLoc + "', '" + dTime + "', '" + dInstructions + "', '" + pLoc + "', '" + pTime + "', '" + pInstructions + "', '" + hospitalName + "', '" + comments + "', 0, '')")
        
        connection.commit()

        # create/edit ics file
        c = Calendar()
        e = Event()
        e.name = hospitalName+" Station Appointment"
        e.begin = dTime
        e.end = pTime
        e.description = "Drop Off Location: "+dLoc

        if dInstructions != "":
            e.description += "\nDrop Off Instructions: "+dInstructions
        e.description += "\nPick Up Location: "+pLoc

        if pInstructions != "":
            e.description += "\nPick Up Instructions: "+pInstructions
        if comments != "":
            e.description += "\nFurther Comments: "+comments

        c.events.add(e)
        c.events
        with open('appointment.ics', 'w') as my_file:
            my_file.writelines(c.serialize_iter())

        sendMail("appointment.ics", 0)

        return redirect("/home")

    return render_template('appointment.html')


# edit appointment
    # send email to user with updated ics file
@app.route('/editappointment/<appid>', methods=['GET', 'POST'])
def editAppointment(appid):
    if session.get('username') == None:
        return redirect('/')
    # cursor = connection.cursor()
    if request.method == 'POST':

        current=request.form['dLoc']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET dLoc = '"+current+"' WHERE appointmentid = "+appid)
  
        current=request.form['dTime']
        if current != "":
            cursor.execute("UPDATE appointments SET dTime = '"+current+"' WHERE appointmentid = "+appid)

        current=request.form['dInstructions']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET dInstructions = '"+current+"' WHERE appointmentid = "+appid)

        current=request.form['pLoc']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET pLoc = '"+current+"' WHERE appointmentid = "+appid)

        current=request.form['pTime']
        if current != "":
            cursor.execute("UPDATE appointments SET pTime = '"+current+"' WHERE appointmentid = "+appid)

        current=request.form['pInstructions']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET pInstructions = '"+current+"' WHERE appointmentid = "+appid)
 
        current=request.form['hospitalName']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET hospitalName = '"+current+"' WHERE appointmentid = "+appid)

        current=request.form['comments']
        current = fixstring(current)
        if current != "":
            cursor.execute("UPDATE appointments SET comments = '"+current+"' WHERE appointmentid = "+appid)

        connection.commit()

        return redirect('/home')
    cursor.execute("SELECT * FROM appointments WHERE appointmentid = "+str(appid))
    appointmentInfo = cursor.fetchone()

    return render_template('editappointment.html', appointmentInfo=appointmentInfo)


# allows users to log out of the website
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# create machines with unique ids
    # keep as separate page
@app.route('/addstation', methods=['GET','POST'])
def addstation():
    if session.get('username') == None:
        return redirect('/')

    if request.method == 'POST':
        id = request.form['stationid']

        cursor.execute("SELECT stationID FROM stations")
        ids = cursor.fetchall()

        list_ids = []

        for thisid in ids:
            list_ids.append(thisid['stationID'])
        
        if id in list_ids:
            flash("ID Already In Use")

            return redirect('/addstation')

        cursor.execute("INSERT INTO stations VALUES('"+id+"', '', 0)")

        connection.commit()

        return redirect('/home')

    return render_template('addstation.html')


# delete an appointment
@app.route('/deleteappointment', methods=['GET','POST'])
def deleteapp():
    if session.get('username') == None:
        return redirect('/')

    # cursor = connection.cursor()
    appid = request.form['appID']
    cursor.execute("DELETE FROM appointments WHERE appointmentid = "+appid) # delete the machines

    cursor.execute("DELETE FROM paired WHERE appid = '"+appid+"'")
    connection.commit()
    return redirect('/home')


# view all past appointments
    # keep separate
@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':

        it = request.form['inputtype']

        if it == "1":
        # method for updating comments on individual updates
            pastid = request.form['pastid']
            comments = request.form['comments']
            comments = fixstring(comments)

            cursor.execute("UPDATE pastAppointments SET feedback = '"+comments+"' WHERE pastid = "+pastid)
            connection.commit()
        elif it == "2":
            # method for deleting individual appointments
            pastid = request.form['id']
            cursor.execute("DELETE FROM pastAppointments WHERE pastid = "+pastid)
            connection.commit()

        return redirect('/history')

    cursor.execute("SELECT * FROM pastAppointments ORDER BY appday DESC")
    previous = cursor.fetchall()

    cursor.execute("SELECT * FROM brokenMachinesRecord WHERE appid IN (SELECT pastid FROM pastAppointments)")
    previousbroken = cursor.fetchall()
    return render_template('history.html', previous=previous, previousbroken=previousbroken)

# in the future make it more secure, and double check stuff like usernames, emails addresses, and especially passwords
# also consider adding a way to edit/delete users
@app.route('/adduser', methods=['GET','POST'])
def adduser():
    if session.get('username') == None:
        return redirect('/')
    if request.method == 'POST':

        username = request.form["username"]
        cursor.execute("SELECT username FROM users")
        usernames = cursor.fetchall()
        
        list_usernames = []

        for thisusername in usernames:
            list_usernames.append(thisusername['username'])
        
        if username in list_usernames:
            return redirect('/adduser')

        password = request.form["password"]
        email = request.form["email"]

        cursor.execute("INSERT INTO users VALUES('"+ email +"', '"+ username +"', '"+ password +"')")

        connection.commit()
        return redirect("/home")

    return render_template("adduser.html")



# The following are essentially the same code for 5 different uses. In the future I want to replace all of them with popups.
@app.route("/deleteHistory/<appid>", methods=['GET', 'POST'])
def deleteHistory(appid):
    if session.get('username') == None:
        return redirect('/home')
    if request.method == 'POST':
        id = request.form['id']

        cursor.execute("DELETE FROM pastAppointments WHERE pastid = "+str(id))

        connection.commit()

        return redirect('/history')

    return render_template('deleteHistory.html', appid=appid)

@app.route("/deleteStation/<stationid>", methods=['GET', 'POST'])
def deleteStation(stationid):
    if session.get('username') == None:
        return redirect('/home')
    if request.method == 'POST':
        id = request.form['id']

        cursor.execute("DELETE FROM stations WHERE stationID = '"+str(id)+"'")

        connection.commit()

        return redirect('/home')

    return render_template('deleteStation.html', stationid=stationid)

@app.route("/passedInspection/<stationid>", methods=['GET', 'POST'])
def passedInspection(stationid):
    if session.get('username') == None:
        return redirect('/home')

    if request.method == 'POST':
        id = request.form['id']

        cursor.execute("UPDATE stations SET stage = 0 WHERE stationID = '"+ id +"'")

        connection.commit()

        return redirect('/home')

    return render_template('passedInspection.html', stationid=stationid)

@app.route("/reportbroken/<appid>", methods=['GET', 'POST'])
def reportBroken(appid):
    if session.get('username') == None:
        return redirect('/home')

    if request.method == 'POST':
        appid = request.form['appID']

        cursor.execute("SELECT * FROM paired WHERE appid = "+str(appid))

        paired = cursor.fetchone()

        cursor.execute("SELECT * FROM stations WHERE stationID = '"+paired['machineid']+"'")
        station = cursor.fetchone()

        cursor.execute("INSERT INTO brokenMachinesRecord VALUES('"+ paired['machineid'] +"', '"+ str(paired['appid']) +"')")

        cursor.execute("UPDATE stations SET stage = 5 WHERE stationID = '"+paired['machineid']+"'")

        cursor.execute("UPDATE appointments SET status = 0 WHERE appointmentid = "+str(appid))

        cursor.execute("DELETE FROM paired WHERE appid = "+str(appid))

        connection.commit()

        return redirect('/home')
    
    cursor.execute("SELECT * FROM paired WHERE appid = "+str(appid))

    paired = cursor.fetchone()

    return render_template('broken.html', appid=appid, stationid=paired['machineid'])

@app.route("/deleteAppointment/<appid>", methods=['GET', 'POST'])
def deleteAppointment(appid):
    if session.get('username') == None:
        return redirect('/home')

    if request.method == 'POST':

        id = request.form['id']

        cursor.execute("DELETE FROM appointments WHERE appointmentid = '"+str(id)+"'")

        connection.commit()

        return redirect('/home')

    return render_template('deleteappointment.html', appid=appid)


if __name__ == "__main__":
    app.run()
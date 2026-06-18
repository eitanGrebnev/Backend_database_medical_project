from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import sqlite3
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def is_strong_password(password):
    if len(password) < 8:
        return False
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)
    has_special = any(char in "!@#?" for char in password)
    return has_upper and has_lower and has_letter and has_number and has_special


def create_patient(tokens):
    # create_patient <username> <password>
    if len(tokens) != 3:
        print("Create patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    if not is_strong_password(password):
        print('Create patient failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from "!", "@", "#", "?")')
        return

    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again")
        return
    


    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except sqlite3.Error as e:
        print("Create patient failed")
        return
    except Exception as e:
        print("Create patient failed")
        return
    print("Created user", username)



def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the lngth for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Create caregiver failed")
        return

    username = tokens[1]
    password = tokens[2]

    #to ensure password has enough security and before we check
    if not is_strong_password(password):
        print('Create caregiver failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from "!", "@", "#", "?")')
        return

    
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again")
        return
    



    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)


    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except sqlite3.Error as e:
        print("Create caregiver failed")
        return
    except Exception as e:
        print("Create caregiver failed")
        return
    print("Created user", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except sqlite3.Error as e:
        print("Login patient failed")
        return
    except Exception as e:
        print("Login patient failed")
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information ( incl operation name)
    if len(tokens) != 3:
        print("Login caregiver failed")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except sqlite3.Error as e:
        print("Login caregiver failed")
        return
    except Exception as e:
        print("Login caregiver failed")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login caregiver failed")
    else:
        print("Logged in as " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # search_caregiver_schedule <date>
    # Both patients and caregivers can perform this operation.
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    # check: length needs to be exactly 2 (operation + date)
    if len(tokens) != 2:
        print("Please try again")
        return

    # check: date must be yyyy-mm-dd
    date = tokens[1]
    date_tokens = date.split("-")
    try:
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
    except Exception:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()
    #Output the username for the caregivers that are available for the date ordered alphabetically by the username of the caregiver.
        # caregivers available for this date, ordered alphabetically
        get_caregivers = "SELECT Username FROM Availabilities WHERE Time = ? ORDER BY Username"
        cursor.execute(get_caregivers, (d,))
        caregivers = [row['Username'] for row in cursor]

        # vaccines and available doses
        get_vaccines = "SELECT Name, Doses FROM Vaccines ORDER BY Name"
        cursor.execute(get_vaccines)
        vaccines = [(row['Name'], row['Doses']) for row in cursor]

        print("Caregivers:")
        if len(caregivers) == 0:
            print("No caregivers available")
        else:
            for caregiver_username in caregivers:
                print(caregiver_username)

        print("Vaccines:")
        if len(vaccines) == 0:
            print("No vaccines available")
        else:
            for vaccine_name, doses in vaccines:
                print(str(vaccine_name) + " " + str(doses))
    except sqlite3.Error:
        print("Please try again")
    except Exception:
        print("Please try again")
    finally:
        cm.close_connection()





def reserve(tokens):
    # reverve <date> <vaccine>
    # 2nd  need ot chekc if theyre logged in as a patient
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    if current_patient is None:
        print("Please login as a patient")
        return

    # also  need to check if the length of tokens is 3, which is the operation name, date and vaccine name
    if len(tokens) != 3:
        print("Please try again")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    #  format yyyy-mm-dd   
    date_tokens = date.split("-")

    try:
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
    except Exception:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        # pick available caregiver alphabetically for this date
        get_caregiver = "SELECT Username FROM Availabilities WHERE Time = ? ORDER BY Username LIMIT 1"
        cursor.execute(get_caregiver, (d,))
        caregiver_row = cursor.fetchone()
        if caregiver_row is None:
            print("No caregiver is available")
            return
        caregiver_username = caregiver_row['Username']

        # check vaccine doses
        get_vaccine = "SELECT Doses FROM Vaccines WHERE Name = ?"
        cursor.execute(get_vaccine, (vaccine_name,))
        vaccine_row = cursor.fetchone()
        if vaccine_row is None or vaccine_row['Doses'] <= 0:
            print("Not enough available doses")
            return

        # insert appointment, remove availability, decrement doses
        add_appointment = "INSERT INTO Appointments (Time, PatientUsername, CaregiverUsername, VaccineName) VALUES (?, ?, ?, ?)"
        cursor.execute(add_appointment, (d, current_patient.get_username(), caregiver_username, vaccine_name))
        appointment_id = cursor.lastrowid

        remove_availability = "DELETE FROM Availabilities WHERE Time = ? AND Username = ?"
        cursor.execute(remove_availability, (d, caregiver_username))

        update_vaccine = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = ?"
        cursor.execute(update_vaccine, (vaccine_name,))

        conn.commit()
        print("Appointment ID " + str(appointment_id) + ", Caregiver username " + caregiver_username)
    except sqlite3.Error as e:
        conn.rollback()
        print("Please try again")
    except Exception as e:
        conn.rollback()
        print("Please try again")
    finally:
        cm.close_connection()



def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    try:
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
        current_caregiver.upload_availability(d)
    except sqlite3.Error as e:
        print("Upload Availability Failed")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        return
    print("Availability uploaded!")


def cancel(tokens):
    # cancel <appointment_id>
    # 1st we need to check if the user is logged in as a patient, 
    #what I'm thinking is that we check the database for existing appointments with appointment ID and delete it if it exists, and if it doesn't then we print error and what are the closest dates to that one
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return
    if len(tokens) != 2:
        print("Please try again")
        return

    appointment_id = tokens[1]
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        get_appointment = "SELECT AppointmentID, Time, CaregiverUsername, VaccineName FROM Appointments WHERE AppointmentID = ?"
        cursor.execute(get_appointment, (appointment_id,))
        appointment = cursor.fetchone()

        if appointment is None:
            print("Appointment ID " + str(appointment_id) + " does not exist")
            return

        remove_appointment = "DELETE FROM Appointments WHERE AppointmentID = ?"
        cursor.execute(remove_appointment, (appointment_id,))

        update_vaccine = "UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = ?"
        cursor.execute(update_vaccine, (appointment['VaccineName'],))

        add_back_availability = "INSERT INTO Availabilities VALUES (?, ?)"
        cursor.execute(add_back_availability, (appointment['Time'], appointment['CaregiverUsername']))

        conn.commit()
        print("Appointment ID " + str(appointment_id) + " has been successfully canceled")
    except sqlite3.Error as e:
        conn.rollback()
        print("Please try again")
        return
    except Exception as e:
        conn.rollback()
        print("Please try again")
        return
    finally:
        cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except sqlite3.Error as e:
        print("Error occurred when adding doses")
        return
    except Exception as e:
        print("Error occurred when adding doses")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    print("Doses updated!")


def show_appointments(tokens):


#step 1: check if the user is logged in as a patient
    global current_patient
    global current_caregiver
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    # check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()
        if current_patient is not None:
            get_appointments = "SELECT AppointmentID, VaccineName, Time, CaregiverUsername FROM Appointments WHERE PatientUsername = ? ORDER BY AppointmentID"
            cursor.execute(get_appointments, (current_patient.get_username(),))
        else:
            get_appointments = "SELECT AppointmentID, VaccineName, Time, PatientUsername FROM Appointments WHERE CaregiverUsername = ? ORDER BY AppointmentID"
            cursor.execute(get_appointments, (current_caregiver.get_username(),))

        appointments = list(cursor)
    except sqlite3.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        return
    finally:
        cm.close_connection()

    if len(appointments) == 0:
        print("No appointments scheduled")
    else:
        for appointment in appointments:
            appointment_date = str(appointment['Time']).split(" ")[0]
            if current_patient is not None:
                print(str(appointment['AppointmentID']) + " " + str(appointment['VaccineName']) + " " + appointment_date + " " + str(appointment['CaregiverUsername']))
            else:
                print(str(appointment['AppointmentID']) + " " + str(appointment['VaccineName']) + " " + appointment_date + " " + str(appointment['PatientUsername']))

    

def logout(tokens):
    global current_patient
    global current_caregiver
    try:
        if current_patient is None and current_caregiver is None:
            print("Please login first")
            return
        elif len(tokens) != 1:
            print("Please try again")
            return

        current_patient = None
        current_caregiver = None
        print("Successfully logged out")
    except sqlite3.Error as e:
        print("Please try again")
    except Exception as e:
        print("Please try again")



def start():
    stop = False
    print("*** Please enter one of the following commands ***")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        tokens = response.split()
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

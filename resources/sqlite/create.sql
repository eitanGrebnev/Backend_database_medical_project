CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);


CREATE TABLE Patients (   
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);


CREATE TABLE Appointments  (
    AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    Time date,
    PatientUsername varchar(255) REFERENCES Patients,
    CaregiverUsername varchar(255) REFERENCES Caregivers,
    VaccineName varchar(255) REFERENCES Vaccines
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);
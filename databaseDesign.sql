
-- CREATE DATABASE appointments;
-- USE appointments;
DROP TABLE IF EXISTS users;
CREATE TABLE users(
    userEmail VARCHAR(50) UNIQUE,
    username VARCHAR(20) UNIQUE,
    `password` VARCHAR(20)
    -- email VARCHAR(20)
);


DROP TABLE IF EXISTS stations;
CREATE TABLE stations(
    stationID VARCHAR(12) UNIQUE,
    loc VARCHAR(100),
    stage INT -- 0=in warehouse, 1=in transit to appointment, 2=at appointment, 3=picked up, 4=need inspection
);

DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments(
    appointmentid INT UNIQUE,
    dLoc VARCHAR(100),
    -- dTime SMALLDATETIME,
    dTime VARCHAR(16),
    dInstructions VARCHAR(200),
    pLoc VARCHAR(100),
    -- pTime SMALLDATETIME,
    pTime VARCHAR(16),
    pInstructions VARCHAR(200),
    hospitalName VARCHAR(50),
    `comments` VARCHAR(200),
    `status` INT, -- 0=scheduled, 1=en route, 2=dropped off, 3=picked up
    machine VARCHAR(12)
);

DROP TABLE IF EXISTS paired;
CREATE TABLE paired(
    appid INT UNIQUE,
    machineid VARCHAR(12) UNIQUE,
    FOREIGN KEY (appid)
        REFERENCES appointments(appointmentid)
        ON DELETE CASCADE,
    FOREIGN KEY (machineid)
        REFERENCES stations(stationID)
        ON DELETE CASCADE
);


DROP TABLE IF EXISTS pastAppointments;
CREATE TABLE pastAppointments(
    pastid INT,
    statid VARCHAR(12),
    appday VARCHAR(16),
    hospital VARCHAR(50),
    feedback VARCHAR(1000)
);

DROP TABLE IF EXISTS brokenMachinesRecord;
CREATE TABLE brokenMachinesRecord(
    idstation VARCHAR(12),
    appid INT
);

INSERT INTO stations VALUES
    ("anid", "here", 0),
    ("anotherid", "there", 0)
;
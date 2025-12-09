-- DROP DATABASE HotelDB;
CREATE DATABASE IF NOT EXISTS HotelDB;

USE HotelDB;

CREATE TABLE Role (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Description TEXT
);

CREATE TABLE Customer (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    UserName VARCHAR(25) NOT NULL UNIQUE,
    FullName VARCHAR(100),
    Balance INT NOT NULL DEFAULT 0,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20),
    HashPassword VARCHAR(255) NOT NULL,
    RoleID INT NOT NULL,
    CONSTRAINT FK_Customer_Role FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
);

CREATE TABLE Staff (
    StaffID INT PRIMARY KEY,
    HireDate DATE NOT NULL,
    Salary INT,
    IsActive BOOLEAN DEFAULT TRUE,
	CONSTRAINT FK_Staff_Customer FOREIGN KEY (StaffID) REFERENCES Customer(CustomerID)
);

CREATE TABLE RoomType (
    RoomTypeID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Description TEXT,
    Price INT NOT NULL,
    MaxPeople INT NOT NULL,
    BedCount INT NOT NULL
);

CREATE TABLE `Status` (
    StatusID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL UNIQUE,
    Type VARCHAR(50),
    Description TEXT
);

CREATE TABLE Room (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomNumber VARCHAR(10) NOT NULL UNIQUE,
    RoomTypeID INT NOT NULL,
    StatusID INT,
    FOREIGN KEY (RoomTypeID) REFERENCES RoomType(RoomTypeID),
    FOREIGN KEY (StatusID) REFERENCES `Status`(StatusID)
);

CREATE TABLE `Transaction` (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    CheckIn DATETIME NOT NULL,
    CheckOut DATETIME NOT NULL,
    TotalPrice INT DEFAULT 0,
    PaidAt DATETIME,
    `Status` VARCHAR(30),
    CreateAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

CREATE TABLE TransactionRoom (
    TransactionID INT NOT NULL,
    RoomID INT NOT NULL,
    PRIMARY KEY (TransactionID, RoomID),
    FOREIGN KEY (TransactionID) REFERENCES Transaction(TransactionID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

CREATE TABLE Review (
    ReviewID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    RoomID INT NOT NULL,
    Rating TINYINT CHECK (Rating BETWEEN 1 AND 5),
    ReviewText TEXT,
    CreateAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID)
);

CREATE TABLE Incident (
    IncidentID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    RoomID INT NOT NULL,
    StatusID INT NOT NULL,
    Description TEXT,
    CreateAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
    FOREIGN KEY (StatusID) REFERENCES `Status`(StatusID)
);

INSERT INTO Role (Name, Description) VALUES
('Customer', 'Normal hotel customer'),
('Staff', 'Hotel staff member'),
('Manager', 'Hotel manager'),
('Admin', 'System administrator'),
('Cleaner', 'Room cleaning staff');

INSERT INTO Customer (FullName, UserName, Email, PhoneNumber, HashPassword, RoleID) VALUES
('Alice Nguyen', 'AliceNguyen', 'alice@example.com', '0901234567', 'hash1', 1),
('Bob Tran', 'BobTran', 'bob@example.com', '0902234567', 'hash2', 1),
('Chris Pham', 'ChrisPham', 'chris@example.com', '0903234567', 'hash3', 2),
('David Hoang', 'DavidHoang', 'david@example.com', '0904234567', 'hash4', 3),
('Emily Le', 'EmilyLe', 'emily@example.com', '0905234567', 'hash5', 5);

INSERT INTO Staff (StaffID, HireDate, Salary, IsActive) VALUES
(3, '2023-01-01', 8000000, TRUE),
(4, '2022-06-15', 15000000, TRUE),
(5, '2023-04-10', 6000000, TRUE),
(2, '2024-01-05', 5000000, FALSE),
(1, '2021-11-20', 7000000, TRUE);

INSERT INTO RoomType (Name, Description, Price, MaxPeople, BedCount) VALUES
('Standard', 'Basic room for 2 people', 500000, 2, 1),
('Deluxe', 'Larger room with balcony', 800000, 3, 2),
('Suite', 'Luxury room with living area', 1500000, 4, 2),
('Family', 'Room for families', 1200000, 5, 3),
('VIP', 'Premium top-floor room', 2500000, 4, 2);

INSERT INTO `Status` (Name, Type, Description) VALUES
('Available', 'Room', 'Room is empty'),
('Booked', 'Room', 'Customer booked but not checked in'),
('Occupied', 'Room', 'Currently used'),
('Cleaning', 'Room', 'Room is being cleaned'),
('Maintenance', 'Room', 'Room requires maintenance'),
('Reported', 'Incident', 'Issue reported'),
('In Progress', 'Incident', 'Staff fixing problem'),
('Resolved', 'Incident', 'Issue resolved');

INSERT INTO Room (RoomNumber, RoomTypeID, StatusID) VALUES
('A101', 1, 1),
('A102', 1, 1),
('B201', 2, 1),
('B202', 3, 1),
('C301', 5, 1);

INSERT INTO `Transaction` (CustomerID, CheckIn, CheckOut, PaidAt, Status) VALUES
(1, '2024-12-01 12:00:00', '2024-12-02 12:00:00', '2024-12-01 10:00:00', 'Paid'),
(2, '2024-12-02 14:00:00', '2024-12-03 11:00:00', '2024-12-02 12:30:00', 'Pending'),
(3, '2024-12-03 15:00:00', '2024-12-04 12:00:00', '2024-12-03 15:00:00', 'Paid'),
(4, '2024-12-04 16:00:00', '2024-12-05 10:00:00', NULL, 'Unpaid'),
(5, '2024-12-05 08:00:00', '2024-12-06 12:00:00', '2024-12-05 09:00:00', 'Paid');

INSERT INTO TransactionRoom (TransactionID, RoomID)
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);

INSERT INTO Review (CustomerID, RoomID, Rating, ReviewText) VALUES
(1, 1, 4, 'Nice room, comfortable bed'),
(2, 2, 5, 'Excellent stay!'),
(3, 3, 3, 'Average experience'),
(4, 4, 2, 'Room was noisy'),
(5, 5, 5, 'Amazing luxury experience');

INSERT INTO Incident (CustomerID, RoomID, StatusID, Description) VALUES
(1, 1, 6, 'Broken lamp'),               -- Reported
(2, 2, 6, 'Air conditioner broken'),    -- Reported
(3, 3, 7, 'Shower broken'),             -- In Progress
(4, 4, 8, 'Room issue resolved'),       -- Resolved
(5, 5, 6, 'TV requires maintenance');   -- Reported

-- select * from Customer
-- select * from RoomType
-- select * from Room where RoomTypeID = 1
-- select * from TransactionRoom
-- select * from Transaction

-- truncate TransactionRoom
-- truncate Transaction

-- insert into `Transaction` (CustomerID, CheckIn, CheckOut, PaidAt, Status) VALUES
-- (1, '2025-12-01 12:00:00', '2025-12-02 12:00:00', NULL, 'Paid')


DELIMITER //

CREATE TRIGGER trg_update_total_price_after_insert
AFTER INSERT ON TransactionRoom
FOR EACH ROW
BEGIN
    DECLARE room_price DECIMAL(10,2);

    -- Lấy giá phòng theo RoomID
    SELECT Price INTO room_price
    FROM Room r
    JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
    WHERE r.RoomID = NEW.RoomID;

    -- Tính số đêm
    UPDATE `Transaction`
    SET TotalPrice = TotalPrice + (
        room_price * DATEDIFF(CheckOut, CheckIn)
    )
    WHERE TransactionID = NEW.TransactionID;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_update_total_price_after_delete
AFTER DELETE ON TransactionRoom
FOR EACH ROW
BEGIN
    DECLARE room_price DECIMAL(10,2);

    SELECT Price INTO room_price
    FROM Room r
    JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
    WHERE r.RoomID = OLD.RoomID;

    UPDATE `Transaction`
    SET TotalPrice = TotalPrice - (
        room_price * DATEDIFF(CheckOut, CheckIn)
    )
    WHERE TransactionID = OLD.TransactionID;
END//

DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_update_total_price_after_update
AFTER UPDATE ON TransactionRoom
FOR EACH ROW
BEGIN
    DECLARE old_price DECIMAL(10,2);
    DECLARE new_price DECIMAL(10,2);

    -- Giá cũ
    SELECT Price INTO old_price
    FROM Room r
    JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
    WHERE r.RoomID = OLD.RoomID;

    -- Giá mới
    SELECT Price INTO new_price
    FROM Room r
    JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
    WHERE r.RoomID = NEW.RoomID;

    UPDATE `Transaction`
    SET TotalPrice = TotalPrice + (
        (new_price - old_price) * DATEDIFF(CheckOut, CheckIn)
    )
    WHERE TransactionID = NEW.TransactionID;
END//

DELIMITER ;


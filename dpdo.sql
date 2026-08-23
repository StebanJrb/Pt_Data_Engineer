USE dpdo;

CREATE TABLE Position (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE City (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL UNIQUE,
    IsContestEnabled BIT NOT NULL DEFAULT 0
);

CREATE TABLE Category (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL UNIQUE,
    MaxCapacity INT NOT NULL CHECK (MaxCapacity > 0)
);

CREATE TABLE Event (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Date DATE NOT NULL
);

CREATE TABLE Employee (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    PositionId INT NOT NULL,
    CityId INT NOT NULL,
    CONSTRAINT FK_Employee_Position FOREIGN KEY (PositionId) REFERENCES Position(Id),
    CONSTRAINT FK_Employee_City FOREIGN KEY (CityId) REFERENCES City(Id)
);

CREATE TABLE Registration (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeId INT NOT NULL,
    CategoryId INT NOT NULL,
    RegistrationDate DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Registration_Employee FOREIGN KEY (EmployeeId) REFERENCES Employee(Id),
    CONSTRAINT FK_Registration_Category FOREIGN KEY (CategoryId) REFERENCES Category(Id),
    CONSTRAINT UQ_Employee_Category UNIQUE (EmployeeId, CategoryId)
);

CREATE TABLE Result (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    RegistrationId INT NOT NULL UNIQUE,
    Score DECIMAL(5,2) NOT NULL,
    CONSTRAINT FK_Result_Registration FOREIGN KEY (RegistrationId) REFERENCES Registration(Id)
);

CREATE TABLE RegistrationAttempt (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    AttemptedEmployeeId INT NULL,
    CategoryId INT NULL,
    RejectionReason VARCHAR(50) NOT NULL,
    AttemptDate DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Attempt_Category FOREIGN KEY (CategoryId) REFERENCES Category(Id)
);

CREATE INDEX IX_Registration_Category ON Registration(CategoryId);

CREATE INDEX IX_Registration_Employee ON Registration(EmployeeId);

CREATE INDEX IX_Employee_City ON Employee(CityId);

CREATE INDEX IX_Attempt_Category ON RegistrationAttempt(CategoryId);
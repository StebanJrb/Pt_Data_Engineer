from django.db import connection
from django.test.runner import DiscoverRunner

# Mirrors SQL_Scripts/dpdo.sql. DPDO_API models are managed = False (their
# real tables live in SQL Server, created by that script, not by Django
# migrations), so 'migrate' never creates them in the test database. The
# IF OBJECT_ID guards make this safe to re-run against a database kept
# around with 'manage.py test --keepdb'.
TABLE_STATEMENTS = [
    """
    IF OBJECT_ID('Position', 'U') IS NULL
    BEGIN
        CREATE TABLE Position (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(50) NOT NULL UNIQUE
        )
    END
    """,
    """
    IF OBJECT_ID('City', 'U') IS NULL
    BEGIN
        CREATE TABLE City (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(100) NOT NULL UNIQUE,
            IsContestEnabled BIT NOT NULL DEFAULT 0
        )
    END
    """,
    """
    IF OBJECT_ID('Category', 'U') IS NULL
    BEGIN
        CREATE TABLE Category (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(100) NOT NULL UNIQUE,
            MaxCapacity INT NOT NULL CHECK (MaxCapacity > 0)
        )
    END
    """,
    """
    IF OBJECT_ID('Event', 'U') IS NULL
    BEGIN
        CREATE TABLE Event (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(150) NOT NULL,
            Date DATE NOT NULL
        )
    END
    """,
    """
    IF OBJECT_ID('Employee', 'U') IS NULL
    BEGIN
        CREATE TABLE Employee (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name VARCHAR(150) NOT NULL,
            PositionId INT NOT NULL,
            CityId INT NOT NULL,
            CONSTRAINT FK_Employee_Position FOREIGN KEY (PositionId) REFERENCES Position(Id),
            CONSTRAINT FK_Employee_City FOREIGN KEY (CityId) REFERENCES City(Id)
        )
    END
    """,
    """
    IF OBJECT_ID('Registration', 'U') IS NULL
    BEGIN
        CREATE TABLE Registration (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            EmployeeId INT NOT NULL,
            CategoryId INT NOT NULL,
            RegistrationDate DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            CONSTRAINT FK_Registration_Employee FOREIGN KEY (EmployeeId) REFERENCES Employee(Id),
            CONSTRAINT FK_Registration_Category FOREIGN KEY (CategoryId) REFERENCES Category(Id),
            CONSTRAINT UQ_Employee_Category UNIQUE (EmployeeId, CategoryId)
        )
    END
    """,
    """
    IF OBJECT_ID('Result', 'U') IS NULL
    BEGIN
        CREATE TABLE Result (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            RegistrationId INT NOT NULL UNIQUE,
            Score DECIMAL(5,2) NOT NULL,
            CONSTRAINT FK_Result_Registration FOREIGN KEY (RegistrationId) REFERENCES Registration(Id)
        )
    END
    """,
    """
    IF OBJECT_ID('RegistrationAttempt', 'U') IS NULL
    BEGIN
        CREATE TABLE RegistrationAttempt (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            AttemptedEmployeeId INT NULL,
            CategoryId INT NULL,
            RejectionReason VARCHAR(50) NOT NULL,
            AttemptDate DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            CONSTRAINT FK_Attempt_Category FOREIGN KEY (CategoryId) REFERENCES Category(Id)
        )
    END
    """,
]

# Mirrors SQL_Scripts/stored_procedures.sql. Each entry is executed as its
# own batch (CREATE PROCEDURE must be the only statement in its batch).
PROCEDURE_STATEMENTS = [
    "IF OBJECT_ID('sp_GetCategoryWinners', 'P') IS NOT NULL DROP PROCEDURE sp_GetCategoryWinners",
    """
    CREATE PROCEDURE sp_GetCategoryWinners
        @CategoryId INT
    AS
    BEGIN
        SET NOCOUNT ON;
        SELECT TOP 10
            e.Name AS EmployeeName,
            r.Score,
            RANK() OVER (ORDER BY r.Score DESC) AS Position
        FROM Result r
        INNER JOIN Registration reg ON r.RegistrationId = reg.Id
        INNER JOIN Employee e ON reg.EmployeeId = e.Id
        WHERE reg.CategoryId = @CategoryId
        ORDER BY r.Score DESC;
    END
    """,
    "IF OBJECT_ID('sp_GetRegistrationStatistics', 'P') IS NOT NULL DROP PROCEDURE sp_GetRegistrationStatistics",
    """
    CREATE PROCEDURE sp_GetRegistrationStatistics
    AS
    BEGIN
        SET NOCOUNT ON;

        SELECT e.Name AS EmployeeName, COUNT(reg.Id) AS TotalRegistrations
        FROM Employee e
        INNER JOIN Position p ON e.PositionId = p.Id
        LEFT JOIN Registration reg ON reg.EmployeeId = e.Id
        WHERE p.Name = 'Asesor'
        GROUP BY e.Id, e.Name;

        SELECT COUNT(*) AS UnauthorizedAttempts
        FROM RegistrationAttempt
        WHERE RejectionReason = 'POSITION_NOT_ALLOWED';

        SELECT COUNT(*) AS DuplicateAttempts
        FROM RegistrationAttempt
        WHERE RejectionReason = 'DUPLICATE';
    END
    """,
]


class SqlServerUnmanagedModelsTestRunner(DiscoverRunner):
    """Prepares the throwaway SQL Server test database for 'manage.py test'.

    Django creates and drops the test database itself (this just needs the
    DB_USER login to hold the 'dbcreator' server role -- see SETUP.md), but
    since DPDO_API models are managed = False, migrate never creates their
    tables in it. Right after setup, this recreates those tables and the two
    stored procedures so the ORM and DPDO_API/procedures.py have real objects
    to run against, on the real SQL Server engine.
    """

    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)
        with connection.cursor() as cursor:
            for statement in TABLE_STATEMENTS:
                cursor.execute(statement)
            for statement in PROCEDURE_STATEMENTS:
                cursor.execute(statement)
        return result

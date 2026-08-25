USE dpdo;
GO
-- ----------------------------------------------------------------------------
-- sp_GetCategoryWinners
-- Gives the top 10 category needed, in descengind order
-- with the position alredy calculated using RANK() this is for 
-- let SQL SERVER calculate the result instead of letting Django calculate it
-- ----------------------------------------------------------------------------
IF OBJECT_ID('sp_GetCategoryWinners', 'P') IS NOT NULL
    DROP PROCEDURE sp_GetCategoryWinners;
GO

CREATE PROCEDURE sp_GetCategoryWinners
    @CategoryId INT

AS
BEGIN
    SET NOCOUNT ON;
    -- SET NOCOUNT ON: avoids giving "(N rows affected)" with the result set -- 
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
GO

-- ----------------------------------------------------------------------------
-- sp_GetRegistrationStatistics
-- Gives 3 result distinct result set: 
-- 1. inscriptions per employee (Asesor), 
-- 2. All attempts per unathorized User, 
-- 3. All attempts refused by duplicated .
-- ----------------------------------------------------------------------------
IF OBJECT_ID('sp_GetRegistrationStatistics', 'P') IS NOT NULL
    DROP PROCEDURE sp_GetRegistrationStatistics;
GO

CREATE PROCEDURE sp_GetRegistrationStatistics
AS
BEGIN
    SET NOCOUNT ON;

    -- Result set 1: 
    SELECT e.Name AS EmployeeName, COUNT(reg.Id) AS TotalRegistrations
    FROM Employee e
    INNER JOIN Position p ON e.PositionId = p.Id
    LEFT JOIN Registration reg ON reg.EmployeeId = e.Id
    WHERE p.Name = 'Asesor'
    GROUP BY e.Id, e.Name;

    -- Result set 2:
    SELECT COUNT(*) AS UnauthorizedAttempts
    FROM RegistrationAttempt
    WHERE RejectionReason = 'POSITION_NOT_ALLOWED';

    -- Result set 3:
    SELECT COUNT(*) AS DuplicateAttempts
    FROM RegistrationAttempt
    WHERE RejectionReason = 'DUPLICATE';
END
GO

-- WARNING: Here you should especify the user who will excecute the Stored Procedure as showed in SETUP.md, you can uncomment this code with the correct user
--GRANT EXECUTE ON sp_GetCategoryWinners TO <your_user>;
--GRANT EXECUTE ON sp_GetRegistrationStatistics TO <your_user>;
--GO
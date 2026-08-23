-- Checklist de escenarios cubiertos:
-- Empleados de Medellin y Bogota
-- Una ciudad NO habilitada para el concurso ("ciudad no permitida")
-- Asesores (autorizados) y empleados con otras posiciones (no autorizados)
-- Inscripciones validas en varias categorias, en ambas ciudades
-- Inscripciones duplicadas (auditadas en RegistrationAttempt)
-- Intentos de empleados no autorizados (auditados)
-- Resultados/ganadores en al menos una categoria con más de 3 inscritos, para poder distinguir podio (1-3) del resto (4-10)
-- Evento con fecha futura suficiente para simular inscripciones abiertas y (si mueves la fecha) cerradas

USE dpdo;

INSERT INTO Position (Name) VALUES
    ('Asesor'),        -- Id 1: Unica posicion autorizada a participar
    ('Coordinador'),   -- Id 2: NO autorizada
    ('Director');      -- Id 3: NO autorizada a participar, SI autorizado a modificar fecha del evento

INSERT INTO City (Name, IsContestEnabled) VALUES
    ('Medellin', 1),
    ('Bogota', 1),
    ('Cali', 0);       -- Id 3: existe pero NO participa en este concurso

INSERT INTO Category (Name, MaxCapacity) VALUES
    ('Canto', 5),
    ('Baile', 3),
    ('Ilustración', 10);

-- Evento a 10 días de la ventana de inscripciones abiertas
-- (cierre = Date - 3 días). Para probar el caso "cerradas", corre después:
--   UPDATE Event SET Date = DATEADD(DAY, 1, CAST(GETDATE() AS DATE));
INSERT INTO Event (Name, Date) VALUES
    ('Concurso DPDO 2026', DATEADD(DAY, 10, CAST(GETDATE() AS DATE)));

INSERT INTO Employee (Name, PositionId, CityId) VALUES
    ('Ana Torres',    1, 1),  -- Id 1: Asesor, Medellin
    ('Luis Gómez',    1, 1),  -- Id 2: Asesor, Medellin
    ('Marta Ruiz',    1, 1),  -- Id 3: Asesor, Medellin
    ('Pedro Salas',   1, 1),  -- Id 4: Asesor, Medellin
    ('Diana Ríos',    1, 2),  -- Id 5: Asesor, Bogota
    ('Carlos Vera',   1, 2),  -- Id 6: Asesor, Bogota
    ('Julian Peña',   1, 2),  -- Id 7: Asesor, Bogota
    ('Sofía Rojas',   2, 1),  -- Id 8: Coordinador (NO autorizado), Medellin
    ('Andres Cano',   3, 2),  -- Id 9: Director (NO autorizado a participar), Bogota
    ('Laura Méndez',  1, 3);  -- Id 10: Asesor, pero en Cali (ciudad no habilitada)

INSERT INTO Registration (EmployeeId, CategoryId) VALUES
    (1, 1),  -- Ana      -> Canto
    (2, 1),  -- Luis     -> Canto
    (3, 1),  -- Marta    -> Canto
    (5, 1),  -- Diana    -> Canto
    (6, 1),  -- Carlos   -> Canto
    (4, 2),  -- Pedro    -> Baile
    (7, 2),  -- Julian   -> Baile
    (1, 3);  -- Ana      -> Ilustración (un empleado puede inscribirse en más de una categoría)

INSERT INTO Result (RegistrationId, Score) VALUES
    (1, 88.5),  -- Ana
    (2, 95.0),  -- Luis     -> 1er puesto
    (3, 91.2),  -- Marta
    (4, 93.4),  -- Diana
    (5, 79.8);  -- Carlos

INSERT INTO RegistrationAttempt (AttemptedEmployeeId, CategoryId, RejectionReason) VALUES
    (8, 1, 'POSITION_NOT_ALLOWED'),   -- Sofia es Coordinador, no Asesor
    (9, 2, 'POSITION_NOT_ALLOWED'),   -- Andres es Director, no Asesor
    (1, 1, 'DUPLICATE'),              -- Ana ya estaba inscrita en Canto
    (10, 1, 'CITY_NOT_ALLOWED'),      -- Laura es Asesor valido, pero en Cali (no habilitada)
    (999, 1, 'EMPLOYEE_NOT_FOUND');   -- Id que no existe en Employee -- por eso esta columna no tiene FK obligatoria

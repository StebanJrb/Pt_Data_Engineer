# DPDO Tecnical Test

## Overview



## Implementation plan

- 1. **Setup enviroment** Create the git repo, virtual env, connector of SQL server and dependicies for the project.
- 2. **Model Data** Modelate DataBase tables based in the core entities and problem to solve.
- 3. **SQL Development** Develop DataBase Schema with indexes, Primary Keys, Foreing Keys, Constraints defining 1:M, M:M and others
- 4. **Stored Procedures** Develop Stored Procedures for models in the API to not use SQL statements in the api
- 5. **Django Models** Create teh conection form the api to the DB to use the stored procedures for the main problem
- 6. **Business Logic** Use serializers and define how to handle each opertion 
- 7. **EndPoints** Create and expose endpoint with their own http responses
- 8. **Errors & Test** Develop Test cases and define errors status with http and exceptions
- 9. **Documentation** Create documentation for all project

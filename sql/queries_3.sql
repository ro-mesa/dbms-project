-- ============================================================================
-- COMPLETE DBMS LABS 11 TO 14 IMPLEMENTATION FOR `recipe_portal` (MySQL 8.0)
-- Covers:
--   Lab 11: Stored Procedures (No-param, IN, OUT, View, Rename, Grant, Alter, Drop)
--   Lab 12: Triggers (AFTER INSERT/UPDATE/DELETE, BEFORE/INSTEAD OF, DDL, LOGON)
--   Lab 13: TCL (START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT, Temp Table)
--   Lab 14: DCL (Users, Roles, GRANT, REVOKE, DENY, System Permission Views)
-- ============================================================================

USE recipe_portal;


-- ============================================================================
-- ############################################################################
-- LAB 11: STORED PROCEDURES
-- ############################################################################
-- ============================================================================

-- Clean up existing procedures if re-running this script
DROP PROCEDURE IF EXISTS sp_GetAllRecipes;
DROP PROCEDURE IF EXISTS sp_ShowAllRecipes;
DROP PROCEDURE IF EXISTS sp_GetRecipeByID;
DROP PROCEDURE IF EXISTS sp_AddReview;
DROP PROCEDURE IF EXISTS sp_GetRecipesByDifficulty;
DROP PROCEDURE IF EXISTS sp_GetRecipeCount;

DELIMITER //

-- 1. Simple Stored Procedure (No Parameters): Display all recipes with authors
CREATE PROCEDURE sp_GetAllRecipes()
BEGIN
    SELECT 
        r.recipe_id, 
        r.title, 
        r.prep_time, 
        r.difficulty_level, 
        u.username AS author
    FROM recipes r
    JOIN users u ON r.user_id = u.user_id;
END //

-- 2. Stored Procedure with One IN Parameter (INT): Find recipe by ID
CREATE PROCEDURE sp_GetRecipeByID(IN p_recipe_id INT)
BEGIN
    SELECT * 
    FROM recipes 
    WHERE recipe_id = p_recipe_id;
END //

-- 3. Stored Procedure with Multiple IN Parameters: Insert a new review
CREATE PROCEDURE sp_AddReview(
    IN p_recipe_id INT,
    IN p_user_id INT,
    IN p_rating INT,
    IN p_comment TEXT
)
BEGIN
    INSERT INTO reviews (recipe_id, user_id, rating, comment)
    VALUES (p_recipe_id, p_user_id, p_rating, p_comment);
END //

-- 4. Stored Procedure with One IN Parameter (VARCHAR): Filter by difficulty
CREATE PROCEDURE sp_GetRecipesByDifficulty(IN p_difficulty VARCHAR(20))
BEGIN
    SELECT recipe_id, title, prep_time, servings, difficulty_level
    FROM recipes
    WHERE difficulty_level = p_difficulty;
END //

-- 5. Stored Procedure with OUT Parameter: Count total recipes
CREATE PROCEDURE sp_GetRecipeCount(OUT p_total_count INT)
BEGIN
    SELECT COUNT(*) INTO p_total_count FROM recipes;
END //

DELIMITER ;

-- --- Executing Stored Procedures (Lab 11 Tasks 1–5) ---
-- Note: SQL Server uses `EXEC ProcedureName param;`, MySQL uses `CALL ProcedureName(param);`
CALL sp_GetAllRecipes();
CALL sp_GetRecipeByID(1);
CALL sp_AddReview(1, 4, 5, 'Delicious recipe tested via Stored Procedure!');
CALL sp_GetRecipesByDifficulty('Easy');

-- Executing with an OUTPUT parameter:
CALL sp_GetRecipeCount(@total_recipes);
SELECT @total_recipes AS Total_Recipes_Count;


-- 6. View a Stored Procedure Definition (Lab 11 Task 6)
-- [NOT IMPLEMENTABLE IN MYSQL]: SQL Server uses `EXEC sp_helptext 'sp_GetAllRecipes';`
-- MySQL Equivalent:
SHOW CREATE PROCEDURE sp_GetAllRecipes;


-- 7. Rename a Stored Procedure (Lab 11 Task 7)
-- [NOT IMPLEMENTABLE IN MYSQL]: MySQL has no `RENAME PROCEDURE` or `sp_rename` command.
-- SQL Server Code:
--   EXEC sp_rename 'sp_GetAllRecipes', 'sp_ShowAllRecipes';
-- MySQL Workaround (Drop the old procedure and recreate it under the new name):
DROP PROCEDURE IF EXISTS sp_GetAllRecipes;
DELIMITER //
CREATE PROCEDURE sp_ShowAllRecipes()
BEGIN
    SELECT r.recipe_id, r.title, r.prep_time, r.difficulty_level, u.username AS author
    FROM recipes r
    JOIN users u ON r.user_id = u.user_id;
END //
DELIMITER ;


-- 8. Grant Execution Access to a Stored Procedure (Lab 11 Task 8)
-- Create a user first so GRANT EXECUTE runs cleanly:
CREATE USER IF NOT EXISTS 'chef_app_user'@'localhost' IDENTIFIED BY 'ChefPass123!';
GRANT EXECUTE ON PROCEDURE recipe_portal.sp_ShowAllRecipes TO 'chef_app_user'@'localhost';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'chef_app_user'@'localhost';


-- 9. Modify a Stored Procedure (Lab 11 Task 9)
-- [NOT IMPLEMENTABLE IN MYSQL]: In MySQL, `ALTER PROCEDURE` only changes metadata (like COMMENT),
-- NOT the SQL query body inside BEGIN...END.
-- SQL Server Code:
--   ALTER PROCEDURE sp_ShowAllRecipes AS BEGIN SELECT * FROM recipes ORDER BY title; END;
-- MySQL Workaround (DROP + CREATE with sorted output):
DROP PROCEDURE IF EXISTS sp_ShowAllRecipes;
DELIMITER //
CREATE PROCEDURE sp_ShowAllRecipes()
BEGIN
    SELECT r.recipe_id, r.title, r.prep_time, r.difficulty_level, u.username AS author
    FROM recipes r
    JOIN users u ON r.user_id = u.user_id
    ORDER BY r.title ASC;
END //
DELIMITER ;

CALL sp_ShowAllRecipes();


-- 10. Delete a Stored Procedure (Lab 11 Task 10)
DROP PROCEDURE IF EXISTS sp_AddReview;



-- ============================================================================
-- ############################################################################
-- LAB 12: TRIGGERS (DML, BEFORE/INSTEAD OF, DDL, LOGON)
-- ############################################################################
-- ============================================================================

-- Clean up triggers if re-running
DROP TRIGGER IF EXISTS trg_after_insert_recipe;
DROP TRIGGER IF EXISTS trg_after_update_recipe;
DROP TRIGGER IF EXISTS trg_after_delete_recipe;
DROP TRIGGER IF EXISTS trg_before_insert_recipe;

DELIMITER //

-- 1. AFTER INSERT Trigger (Logs new recipe insertions into `audit_logs`)
-- Note: SQL Server uses `FROM inserted`; MySQL uses `NEW.column` with `FOR EACH ROW`.
CREATE TRIGGER trg_after_insert_recipe
AFTER INSERT ON recipes
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action_type, table_affected, record_id, user_id)
    VALUES ('INSERT', 'recipes', NEW.recipe_id, NEW.user_id);
END //

-- 2. AFTER UPDATE Trigger (Logs recipe edits into `audit_logs`)
CREATE TRIGGER trg_after_update_recipe
AFTER UPDATE ON recipes
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action_type, table_affected, record_id, user_id)
    VALUES ('UPDATE', 'recipes', NEW.recipe_id, NEW.user_id);
END //

-- 3. AFTER DELETE Trigger (Logs recipe deletions into `audit_logs`)
-- Note: SQL Server uses `FROM deleted`; MySQL uses `OLD.column`.
CREATE TRIGGER trg_after_delete_recipe
AFTER DELETE ON recipes
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (action_type, table_affected, record_id, user_id)
    VALUES ('DELETE', 'recipes', OLD.recipe_id, OLD.user_id);
END //

-- 4. BEFORE INSERT Trigger (Replaces SQL Server's `INSTEAD OF INSERT` Validation)
-- [NOT IMPLEMENTABLE IN MYSQL]: MySQL does NOT support `INSTEAD OF` triggers on tables.
-- SQL Server Code (INSTEAD OF INSERT):
--   CREATE TRIGGER trg_instead_of_insert_recipe ON recipes INSTEAD OF INSERT AS
--   BEGIN
--       IF EXISTS (SELECT 1 FROM inserted WHERE prep_time <= 0)
--       BEGIN RAISERROR('Prep time must be > 0', 16, 1); ROLLBACK TRANSACTION; END
--       ELSE INSERT INTO recipes (user_id, title, instructions, prep_time, servings, difficulty_level)
--            SELECT user_id, title, instructions, prep_time, servings, difficulty_level FROM inserted;
--   END;
--
-- MySQL Native Equivalent (`BEFORE INSERT` with `SIGNAL SQLSTATE`):
CREATE TRIGGER trg_before_insert_recipe
BEFORE INSERT ON recipes
FOR EACH ROW
BEGIN
    IF NEW.prep_time <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: Preparation time must be greater than 0 minutes.';
    END IF;
END //

DELIMITER ;

-- 5. Database-Level DDL Trigger (Lab 12 Task 8)
-- [NOT IMPLEMENTABLE IN MYSQL]: MySQL triggers only fire on table DML (INSERT/UPDATE/DELETE).
-- MySQL does NOT support database-level DDL triggers (`FOR CREATE_TABLE, ALTER_TABLE, DROP_TABLE`)
-- or the `EVENTDATA()` XML function.
-- SQL Server Code (For Reference/Viva):
--   CREATE TABLE ddl_audit (event_time DATETIME DEFAULT GETDATE(), username NVARCHAR(100), operation_type NVARCHAR(50), object_name NVARCHAR(100));
--   CREATE TRIGGER trg_ddl_audit ON DATABASE FOR CREATE_TABLE, ALTER_TABLE, DROP_TABLE AS
--   BEGIN
--       INSERT INTO ddl_audit (username, operation_type, object_name)
--       SELECT SYSTEM_USER,
--              EVENTDATA().value('(/EVENT_INSTANCE/EventType)[1]', 'NVARCHAR(50)'),
--              EVENTDATA().value('(/EVENT_INSTANCE/ObjectName)[1]', 'NVARCHAR(100)');
--   END;

-- 6. Server-Level LOGON Trigger (Lab 12 Task 9)
-- [NOT IMPLEMENTABLE IN MYSQL]: MySQL does NOT support `ON ALL SERVER FOR LOGON` triggers,
-- `ORIGINAL_LOGIN()`, or `CONNECTIONPROPERTY('client_net_address')`.
-- SQL Server Code (For Reference/Viva):
--   CREATE TABLE logon_audit (log_id INT PRIMARY KEY IDENTITY(1,1), username NVARCHAR(100), logon_time DATETIME DEFAULT GETDATE(), client_ip NVARCHAR(50));
--   CREATE TRIGGER trg_logon_audit ON ALL SERVER FOR LOGON AS
--   BEGIN
--       INSERT INTO recipe_portal.dbo.logon_audit (username, client_ip)
--       SELECT ORIGINAL_LOGIN(), CONNECTIONPROPERTY('client_net_address');
--   END;

-- --- Testing DML Triggers Safely ---
-- Insert a test recipe (fires BEFORE INSERT validation + AFTER INSERT audit log)
INSERT INTO recipes (user_id, title, instructions, prep_time, servings, difficulty_level)
VALUES (1, 'Trigger Test Omelette', 'Whisk eggs and cook in butter.', 10, 1, 'Easy');

SET @test_rec_id = LAST_INSERT_ID();

-- Update the test recipe (fires AFTER UPDATE audit log)
UPDATE recipes SET prep_time = 12 WHERE recipe_id = @test_rec_id;

-- Delete the test recipe (fires AFTER DELETE audit log)
DELETE FROM recipes WHERE recipe_id = @test_rec_id;

-- Verify all 3 trigger events were automatically recorded in `audit_logs`:
SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 5;



-- ============================================================================
-- ############################################################################
-- LAB 13: TRANSACTION CONTROL LANGUAGE (TCL - COMMIT, ROLLBACK, SAVEPOINT)
-- ############################################################################
-- ============================================================================

-- 1. COMMIT Transaction: Atomic multi-table insert (Recipes + Nutrition)
-- Note: SQL Server uses `BEGIN TRANSACTION;`; MySQL uses `START TRANSACTION;`.
START TRANSACTION;

INSERT INTO recipes (user_id, title, instructions, prep_time, servings, difficulty_level)
VALUES (2, 'Atomic Avocado Toast', 'Mash ripe avocado over toasted sourdough bread.', 10, 1, 'Easy');

SET @atomic_id = LAST_INSERT_ID();

INSERT INTO nutrition (recipe_id, calories, protein, carbs, fats)
VALUES (@atomic_id, 320, 9.00, 34.00, 18.00);

-- Permanently commit both inserts together
COMMIT;

-- Clean up the test dish so database stays clean (optional)
DELETE FROM recipes WHERE recipe_id = @atomic_id;


-- 2. ROLLBACK Transaction: Reverting an accidental inventory mistake
START TRANSACTION;

-- Mistakenly wipe out Flour stock (ingredient_id = 1)
UPDATE ingredients
SET stock_quantity = 0.00
WHERE ingredient_id = 1;

-- Undo the entire transaction before committing
ROLLBACK;

-- Verify Flour stock is completely restored:
SELECT ingredient_id, name, stock_quantity FROM ingredients WHERE ingredient_id = 1;


-- 3. Native SAVEPOINT & Partial Rollback (MySQL Standard SQL)
-- [NOT IMPLEMENTABLE IN MYSQL]: SQL Server's `SAVE TRANSACTION Savepoint1;` and
-- `ROLLBACK TRANSACTION Savepoint1;` syntax is T-SQL specific. MySQL uses `SAVEPOINT` & `ROLLBACK TO`.
START TRANSACTION;

-- Operation A: Valid restock of Mozzarella Cheese (+5 kg)
UPDATE ingredients
SET stock_quantity = stock_quantity + 5.00
WHERE ingredient_id = 2;

-- Create a named savepoint after Operation A
SAVEPOINT after_mozzarella_restock;

-- Operation B: Accidental invalid price on Dark Chocolate
UPDATE ingredients
SET cost_per_unit = 99999.00
WHERE ingredient_id = 6;

-- Roll back ONLY Operation B, keeping Operation A intact
ROLLBACK TO SAVEPOINT after_mozzarella_restock;

-- Commit the remaining valid transaction
COMMIT;

-- Verify Mozzarella updated while Dark Chocolate remained unchanged:
SELECT ingredient_id, name, cost_per_unit, stock_quantity 
FROM ingredients 
WHERE ingredient_id IN (2, 6);


-- 4. Temporary Table Savepoint Simulation (Lab 13 Practice Task Method)
-- Demonstrates the lab manual's temporary backup snapshot approach in MySQL syntax:
-- (SQL Server uses `SELECT * INTO #TempTable FROM Table;`; MySQL uses `CREATE TEMPORARY TABLE`)
START TRANSACTION;

CREATE TEMPORARY TABLE temp_ingredients_snapshot AS
SELECT * FROM ingredients WHERE ingredient_id IN (1, 2);

-- Simulate a bad bulk update
UPDATE ingredients SET cost_per_unit = 1.00 WHERE ingredient_id IN (1, 2);

-- Restore original values from the temporary snapshot table
UPDATE ingredients i
JOIN temp_ingredients_snapshot t ON i.ingredient_id = t.ingredient_id
SET i.cost_per_unit = t.cost_per_unit;

DROP TEMPORARY TABLE temp_ingredients_snapshot;
COMMIT;



-- ============================================================================
-- ############################################################################
-- LAB 14: DATA CONTROL LANGUAGE (DCL - USERS, ROLES, GRANT, REVOKE, DENY)
-- ############################################################################
-- ============================================================================

-- 1. Creating Logins & Users
-- [NOT IMPLEMENTABLE IN MYSQL]: SQL Server separates server authentication (`CREATE LOGIN`)
-- from database user mapping (`CREATE USER x FOR LOGIN x WITH DEFAULT_SCHEMA = dbo;`).
-- MySQL handles both in a single `CREATE USER` statement:
CREATE USER IF NOT EXISTS 'chef_app_user'@'localhost' IDENTIFIED BY 'ChefPass123!';
CREATE USER IF NOT EXISTS 'viewer_app_user'@'localhost' IDENTIFIED BY 'ViewPass123!';
CREATE USER IF NOT EXISTS 'admin_app_user'@'localhost' IDENTIFIED BY 'AdminPass123!';


-- 2. GRANT Object-Level Privileges
-- Grant specific privileges on tables
GRANT SELECT, INSERT, UPDATE ON recipe_portal.recipes TO 'chef_app_user'@'localhost';
GRANT SELECT ON recipe_portal.ingredients TO 'chef_app_user'@'localhost';

-- Grant read-only SELECT access to viewer user
GRANT SELECT ON recipe_portal.recipes TO 'viewer_app_user'@'localhost';
GRANT SELECT, INSERT ON recipe_portal.reviews TO 'viewer_app_user'@'localhost';

-- Grant ALL PRIVILEGES on a table (Lab 14 Scenario 5)
GRANT ALL PRIVILEGES ON recipe_portal.meal_plans TO 'admin_app_user'@'localhost';


-- 3. Role-Based Access Control (RBAC): CREATE ROLE & Assign to Users
-- [NOT IMPLEMENTABLE IN MYSQL]: SQL Server built-in roles (`db_datareader`) and
-- `EXEC sp_addrolemember 'RoleName', 'UserName';` do not exist in MySQL.
-- MySQL 8.0 Native Role Syntax:
CREATE ROLE IF NOT EXISTS 'recipe_moderator';
CREATE ROLE IF NOT EXISTS 'portal_reader';

-- Grant table permissions to roles
GRANT SELECT, UPDATE, DELETE ON recipe_portal.reviews TO 'recipe_moderator';
GRANT SELECT ON recipe_portal.categories TO 'portal_reader';

-- Assign roles to users
GRANT 'recipe_moderator' TO 'chef_app_user'@'localhost';
GRANT 'portal_reader' TO 'viewer_app_user'@'localhost';
SET DEFAULT ROLE ALL TO 'chef_app_user'@'localhost', 'viewer_app_user'@'localhost';


-- 4. REVOKE Privileges (Single, Multiple, Role, and ALL PRIVILEGES)
-- Revoke a single privilege from a user
REVOKE UPDATE ON recipe_portal.recipes FROM 'chef_app_user'@'localhost';

-- Revoke multiple privileges from a user
REVOKE SELECT, INSERT ON recipe_portal.reviews FROM 'viewer_app_user'@'localhost';

-- Revoke privilege from a role
REVOKE DELETE ON recipe_portal.reviews FROM 'recipe_moderator';

-- Revoke ALL PRIVILEGES from a user on a table (Lab 14 Scenario 3)
REVOKE ALL PRIVILEGES ON recipe_portal.meal_plans FROM 'admin_app_user'@'localhost';

FLUSH PRIVILEGES;


-- 5. DENY Command (Lab 14 Task 1 Step 4)
-- [NOT IMPLEMENTABLE IN MYSQL]: MySQL has NO `DENY` keyword. In MySQL, permissions are
-- strictly additive; if a privilege is not granted (or is removed via `REVOKE`), access is denied.
-- SQL Server Code (For Reference/Viva):
--   DENY DELETE ON dbo.recipes TO chef_app_user;
--   DENY UPDATE, DELETE ON dbo.recipes TO viewer_app_user;


-- 6. Viewing Applied DCL Permissions & Roles (Lab 14 Task 1 Step 6)
-- [NOT IMPLEMENTABLE IN MYSQL]: SQL Server queries `sys.database_permissions`,
SELECT 
    FROM_USER AS role_name, 
    TO_USER AS assigned_user, 
    TO_HOST AS host
FROM mysql.role_edges
WHERE TO_USER IN ('chef_app_user', 'viewer_app_user');
-- `sys.database_principals`, and `sys.database_role_members`.
-- MySQL Equivalents:
SHOW GRANTS FOR 'chef_app_user'@'localhost';
SHOW GRANTS FOR 'viewer_app_user'@'localhost';
SHOW GRANTS FOR 'recipe_moderator';

-- Querying MySQL's system privilege catalog tables directly:
SELECT Grantee, Table_schema, Table_name, Privilege_type 
FROM information_schema.TABLE_PRIVILEGES 
WHERE Table_schema = 'recipe_portal';


-- 7. Optional Cleanup of Test Users/Roles (Commented out so permissions remain inspectable)
-- DROP ROLE IF EXISTS 'recipe_moderator', 'portal_reader';
-- DROP USER IF EXISTS 'chef_app_user'@'localhost', 'viewer_app_user'@'localhost', 'admin_app_user'@'localhost';
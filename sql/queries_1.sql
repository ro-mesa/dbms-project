-- in this file all those queries would be written that have been taught in lab 1 - 4 
-- ddl(create databse , table and constraint appliction is done in schema.sql file )
USE recipe_portal;
-- Set character encoding and collation for the entire database
ALTER DATABASE recipe_portal 
CHARACTER SET = utf8mb4 
COLLATE = utf8mb4_unicode_ci;

-- Verify database settings
SELECT default_character_set_name, default_collation_name 
FROM information_schema.SCHEMATA 
WHERE schema_name = 'recipe_portal';
-- Create Index: Optimize search lookups on recipe titles
CREATE INDEX idx_recipe_title ON recipes(title);

-- Drop Index: Remove the index when no longer needed
DROP INDEX idx_recipe_title ON recipes;

-- Alter Table: Add a temporary discount column to ingredients
ALTER TABLE ingredients ADD COLUMN discount_percent DECIMAL(4, 2) DEFAULT 0.00;

-- Alter Table: Drop the column
ALTER TABLE ingredients DROP COLUMN discount_percent;

-- ========================================================================
-- OPTIONAL CLEANUP / DROP COMMANDS (Do not uncomment or ever run them during testing)
-- ========================================================================
-- DROP TABLE audit_logs;
-- DROP DATABASE recipe_portal;


-- dml
-- Handle NULL Values: Find categories that do not have a description provided
SELECT category_id, category_name 
FROM categories 
WHERE description IS NULL;

-- Handle NULL Values: Find categories where a description is present
SELECT category_id, category_name, description 
FROM categories 
WHERE description IS NOT NULL;

-- Use LIMIT: Retrieve the top 3 fastest recipes to prepare
SELECT title, prep_time, difficulty_level 
FROM recipes 
ORDER BY prep_time ASC 
LIMIT 3;

-- drl
-- SELECT DISTINCT: Retrieve all unique difficulty levels currently in use
SELECT DISTINCT difficulty_level 
FROM recipes;

-- SQL Aliases: Use clear aliases for readable columns and short table names
SELECT 
    r.title AS 'Recipe Name', 
    r.prep_time AS 'Duration (Mins)', 
    u.username AS 'Chef Name'
FROM recipes AS r
JOIN users AS u ON r.user_id = u.user_id;

-- SELECT INTO (MySQL Syntax): Copy high-calorie recipes into a separate archive table
CREATE TABLE high_calorie_recipes AS
SELECT recipe_id, calories, protein, carbs, fats 
FROM nutrition 
WHERE calories >= 600;

-- it would be done only to show thw working of querries Verify the copied data, then drop the temporary table:
-- SELECT * FROM high_calorie_recipes;
-- DROP TABLE high_calorie_recipes;

-- sql operators 
-- UNION ALL: Combine all Italian and Fast Food recipe IDs, including overlaps
SELECT recipe_id, 'Italian' AS matched_type 
FROM recipe_categories 
WHERE category_id = 1
UNION ALL
SELECT recipe_id, 'Fast Food' AS matched_type 
FROM recipe_categories 
WHERE category_id = 3;

-- INTERSECT: Find recipes that are categorized as BOTH Italian AND Fast Food
-- SELECT recipe_id FROM recipe_categories WHERE category_id = 1
-- INTERSECT
-- SELECT recipe_id FROM recipe_categories WHERE category_id = 3;
SELECT DISTINCT recipe_id 
FROM recipe_categories 
WHERE category_id = 1 
  AND recipe_id IN (
      SELECT recipe_id 
      FROM recipe_categories 
      WHERE category_id = 3
  );
-- MINUS / EXCEPT: Find recipes in Category 1 (Italian) that are NOT in Category 3 (Fast Food)
-- SELECT recipe_id FROM recipe_categories WHERE category_id = 1
-- EXCEPT
-- SELECT recipe_id FROM recipe_categories WHERE category_id = 3;
-- except and intersect wouldnt run onnt his version of sql so run this instead
SELECT DISTINCT recipe_id 
FROM recipe_categories 
WHERE category_id = 1 
  AND recipe_id NOT IN (
      SELECT recipe_id 
      FROM recipe_categories 
      WHERE category_id = 3
  );
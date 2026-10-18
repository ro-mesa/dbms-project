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

-- [MISSING ADDED] UPDATE: Conditionally modify inventory stock
SET SQL_SAFE_UPDATES = 0;
UPDATE ingredients 
SET stock_quantity = stock_quantity + 15.00 
WHERE ingredient_id = 1;

-- [MISSING ADDED] DELETE: Remove low-rated empty reviews
DELETE FROM reviews 
WHERE rating <= 1 AND (comment IS NULL OR comment = '');
SET SQL_SAFE_UPDATES = 1;
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

-- [MISSING ADDED] WHERE with Special Operator LIKE: Wildcard pattern searching
SELECT recipe_id, title, instructions 
FROM recipes 
WHERE title LIKE '%Cake%';

-- [MISSING ADDED] WHERE with Special Operator BETWEEN & Logical OR & ORDER BY DESC:
SELECT title, prep_time, difficulty_level 
FROM recipes 
WHERE (prep_time BETWEEN 15 AND 35) OR difficulty_level = 'Hard'
ORDER BY prep_time DESC; 

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


-- ========================================================================
--  AGGREGATES, GROUP BY & HAVING
-- ========================================================================

-- GROUP BY & HAVING with Aggregate Functions (COUNT, AVG, MAX, MIN):
SELECT 
    recipe_id, 
    COUNT(review_id) AS total_reviews, 
    ROUND(AVG(rating), 2) AS avg_rating,
    MIN(rating) AS lowest_rating,
    MAX(rating) AS highest_rating
FROM reviews
GROUP BY recipe_id
HAVING total_reviews >= 1
ORDER BY avg_rating DESC;



-- sql operators Arithmetic Operators (+, -, *, /):
-- Calculates total macro grams, net carbs (carbs - fats), and fat calorie percentage
SELECT 
    recipe_id, 
    calories, 
    (protein + carbs + fats) AS total_macro_grams,
    (carbs - fats) AS net_carb_spread,
    ROUND(((fats * 9.0) / calories) * 100, 2) AS fat_calorie_percentage
FROM nutrition
WHERE calories > 300;

SELECT recipe_id, title, prep_time, difficulty_level 
FROM recipes 
WHERE difficulty_level != 'Easy' 
  AND prep_time > 20;



-- ========================================================================
-- 7. SET OPERATORS (UNION, UNION ALL, INTERSECT, EXCEPT)
-- ========================================================================

-- [MISSING ADDED] UNION: Combine results and eliminate duplicates
SELECT r.title, 'Italian' AS category_type
FROM recipes r
JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
WHERE rc.category_id = 1
UNION
SELECT r.title, 'Fast Food' AS category_type
FROM recipes r
JOIN recipe_categories rc ON r.recipe_id = rc.recipe_id
WHERE rc.category_id = 3;

-- UNION ALL: Combine results including duplicates
SELECT recipe_id, 'Italian' AS matched_type 
FROM recipe_categories 
WHERE category_id = 1
UNION ALL
SELECT recipe_id, 'Fast Food' AS matched_type 
FROM recipe_categories 
WHERE category_id = 3;

-- INTERSECT: Find recipes categorized as BOTH Italian AND Fast Food
SELECT DISTINCT recipe_id 
FROM recipe_categories 
WHERE category_id = 1 
  AND recipe_id IN (
      SELECT recipe_id 
      FROM recipe_categories 
      WHERE category_id = 3
  );

-- MINUS / EXCEPT: Find recipes in Category 1 that are NOT in Category 3
SELECT DISTINCT recipe_id 
FROM recipe_categories 
WHERE category_id = 1 
  AND recipe_id NOT IN (
      SELECT recipe_id 
      FROM recipe_categories 
      WHERE category_id = 3
  );

  -- ========================================================================
--  ADVANCED SUBQUERIES (EXISTS, ANY, ALL, IN)
-- ========================================================================

-- [MISSING ADDED] Subquery with EXISTS: Check for existence of records
SELECT u.user_id, u.username, u.email 
FROM users u 
WHERE EXISTS (
    SELECT 1 FROM meal_plans mp WHERE mp.user_id = u.user_id
);

-- [MISSING ADDED] Subquery with ANY: Compare against at least one value
SELECT name, cost_per_unit, type
FROM ingredients
WHERE cost_per_unit < ANY (
    SELECT cost_per_unit FROM ingredients WHERE type = 'Dairy'
);

-- [MISSING ADDED] Subquery with ALL: Compare against every single value
SELECT title, prep_time, difficulty_level
FROM recipes
WHERE prep_time > ALL (
    SELECT prep_time FROM recipes WHERE difficulty_level = 'Easy'
);
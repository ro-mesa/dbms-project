-- In this file all those queries and methods would be implemented that would be taught in lab 6-9
-- lab 7 joins 
-- inner join
SELECT 
    r.title AS 'Recipe Name', 
    r.prep_time AS 'Duration (Mins)', 
    u.username AS 'Chef Name'
FROM recipes AS r
JOIN users AS u ON r.user_id = u.user_id;
-- Left join use case: Find all users, including those who have never created any recipes (their recipe title will show as NULL).
SELECT 
    u.user_id,
    u.username,
    u.role,
    r.title AS 'Recipe Title'
FROM users AS u
LEFT JOIN recipes AS r ON u.user_id = r.user_id;

-- Full outer join: show recipes without reviews and reviews without recipes.
SELECT
    r.recipe_id,
    r.title AS 'Recipe Title',
    rv.review_id,
    rv.rating,
    rv.comment
FROM recipes AS r
LEFT JOIN reviews AS rv ON r.recipe_id = rv.recipe_id

UNION

SELECT
    r.recipe_id,
    r.title AS 'Recipe Title',
    rv.review_id,
    rv.rating,
    rv.comment
FROM reviews AS rv
LEFT JOIN recipes AS r ON r.recipe_id = rv.recipe_id
WHERE r.recipe_id IS NULL;

-- Right join use case: List all categories, including categories that currently have zero recipes assigned to them.
SELECT 
    c.category_id,
    c.category_name,
    rc.recipe_id
FROM recipe_categories AS rc
RIGHT JOIN categories AS c ON rc.category_id = c.category_id;
-- self join Use Case: Find pairs of recipes that have the exact same cooking/preparation time, while ensuring a recipe is not paired with itself (r1.recipe_id < r2.recipe_id).
SELECT 
    r1.title AS 'Recipe 1',
    r2.title AS 'Recipe 2',
    r1.prep_time AS 'Shared Prep Time (Mins)'
FROM recipes AS r1
JOIN recipes AS r2 ON r1.prep_time = r2.prep_time 
                  AND r1.recipe_id < r2.recipe_id;
                  
-- cross join Use Case: Generate every possible combination of recipe difficulty levels and meal types for meal planning.
SELECT DISTINCT 
    r.difficulty_level,
    mp.meal_type
FROM recipes AS r
CROSS JOIN meal_plans AS mp;   

-- LAB 8 SUBQUERIES
-- Single-row subquery: Find all recipes that take strictly longer to prepare than the average prep time across all recipes.
SELECT 
    title, 
    prep_time, 
    difficulty_level 
FROM recipes
WHERE prep_time > (
    -- Inner query returns a single scalar average number
    SELECT AVG(prep_time) 
    FROM recipes
);
-- Multi-row subquery: Find the title and prep time of recipes that have received at least one 5-star review in the reviews table.
SELECT 
    recipe_id, 
    title, 
    prep_time 
FROM recipes
WHERE recipe_id IN (
    -- Inner query returns multiple recipe_ids
    SELECT DISTINCT recipe_id 
    FROM reviews 
    WHERE rating = 5
);
-- Subquery with EXISTS: Find users who have at least one scheduled recipe in meal plans
SELECT 
    u.user_id, 
    u.username, 
    u.email 
FROM users u
WHERE EXISTS (
    -- Evaluates to TRUE as soon as a matching row is found
    SELECT 1 
    FROM meal_plans mp 
    WHERE mp.user_id = u.user_id
); 
-- multirow subquerry with NOT IN: Find all recipes that have never been scheduled in any user's meal plan.
SELECT 
    recipe_id, 
    title, 
    difficulty_level 
FROM recipes
WHERE recipe_id NOT IN (
    -- Subquery returns a list of recipe IDs present in meal plans
    SELECT DISTINCT recipe_id 
    FROM meal_plans
    WHERE recipe_id IS NOT NULL
);
--multi row subquerry with ANY: Find all ingredients whose unit cost is cheaper than at least one item belonging to the 'Dairy' category.
SELECT 
    name AS ingredient_name, 
    type, 
    cost_per_unit 
FROM ingredients
WHERE cost_per_unit < ANY (
    -- Subquery returns unit costs of all Dairy items
    SELECT cost_per_unit 
    FROM ingredients 
    WHERE type = 'Dairy'
);
-- Find recipes that take longer to prepare than at least one recipe categorized as 'Hard' difficulty.
SELECT 
    title, 
    prep_time, 
    difficulty_level 
FROM recipes
WHERE prep_time > ANY (
    -- Subquery returns prep times of all Hard recipes
    SELECT prep_time 
    FROM recipes 
    WHERE difficulty_level = 'Hard'
);
-- multi row subqueery with ALL : Project Use Case: Find recipes that take strictly longer to prepare than every single recipe with an 'Easy' difficulty level.
SELECT 
    title, 
    prep_time, 
    difficulty_level 
FROM recipes
WHERE prep_time > ALL (
    -- Subquery returns all prep times for 'Easy' recipes
    SELECT prep_time 
    FROM recipes 
    WHERE difficulty_level = 'Easy'
);
--Find dishes in the nutrition table that have fewer calories than all recipes tagged as 'Fast Food' (Category ID = 3).
SELECT 
    r.title, 
    n.calories, 
    n.protein 
FROM recipes r
JOIN nutrition n ON r.recipe_id = n.recipe_id
WHERE n.calories < ALL (
    -- Subquery returns calorie counts of all Fast Food recipes
    SELECT n2.calories 
    FROM nutrition n2
    JOIN recipe_categories rc ON n2.recipe_id = rc.recipe_id
    WHERE rc.category_id = 3
);
-- Correlated subquery: Find recipes whose calorie count is higher than the average calories of all recipes with that same difficulty level.
SELECT 
    r1.recipe_id, 
    r1.title, 
    r1.difficulty_level, 
    n1.calories
FROM recipes r1
JOIN nutrition n1 ON r1.recipe_id = n1.recipe_id
WHERE n1.calories > (
    -- Correlated to outer query via r2.difficulty_level = r1.difficulty_level
    SELECT AVG(n2.calories)
    FROM recipes r2
    JOIN nutrition n2 ON r2.recipe_id = n2.recipe_id
    WHERE r2.difficulty_level = r1.difficulty_level
);
-- Nested subquery: Find users who have created recipes that require ingredients categorized as 'Dairy'.
SELECT user_id, username, email 
FROM users 
WHERE user_id IN (
    -- Level 1: Find authors of matching recipes
    SELECT user_id 
    FROM recipes 
    WHERE recipe_id IN (
        -- Level 2 (Innermost): Find recipes containing 'Dairy' ingredients
        SELECT ri.recipe_id 
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        WHERE i.type = 'Dairy'
    )
);

--  LAB 09 ---
-- impilicit index
USE recipe_portal;
-- View the implicit indexes created by table constraints
SHOW INDEX FROM users;


-- clustered indexes: Accelerate recipe search lookups on prep_time.
       -- Demonstrate clustered index creation by altering a table's primary key
       -- (Example on a demonstration table recipe_archive to preserve active relationships):
CREATE TABLE IF NOT EXISTS recipe_archive (
    archive_id INT NOT NULL,
    recipe_name VARCHAR(150),
    archived_date DATE
);
        -- Adding the PRIMARY KEY builds the Clustered Index
ALTER TABLE recipe_archive ADD PRIMARY KEY (archive_id);

-- non clustered index
CREATE INDEX idx_recipes_prep_time ON recipes(prep_time);

-- unique index: Ensure ingredient names remain completely distinct across the pantry catalog.
CREATE UNIQUE INDEX idx_unique_ingredient_name ON ingredients(name);

-- composite index:Accelerate lookups filtering recipes by both difficulty_level and prep_time.
CREATE INDEX idx_difficulty_preptime ON recipes(difficulty_level, prep_time);

-- full text index: Keyword searching across recipe title and cooking instructions
CREATE FULLTEXT INDEX idx_ft_recipe_search ON recipes(title, instructions);
    -- Example test query using the FULLTEXT index:
SELECT title, instructions 
FROM recipes 
WHERE MATCH(title, instructions) AGAINST('mozzarella pasta' IN NATURAL LANGUAGE MODE);

-- function based index: Optimize case-insensitive email searches that use LOWER(email).
CREATE INDEX idx_func_lower_email ON users ((LOWER(email)));
        -- Test query that utilizes the functional index:
SELECT user_id, username, email 
FROM users 
WHERE LOWER(email) = 'ali.culinary@gmail.com';

-- spatial index:Track delivery/chef coordinates in a physical location table.
      -- Step A: Add a spatial POINT column
ALTER TABLE users ADD COLUMN location POINT NOT NULL SRID 0;
      -- Step B: Create the Spatial Index
CREATE SPATIAL INDEX idx_spatial_user_loc ON users(location);


-- bitmap index:
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty_level);
     -- "Native BITMAP indexes are supported in DBMS engines like Oracle for data warehousing. 
     -- MySQL InnoDB utilizes B-Tree indexes instead to achieve index-based lookups on discrete values."


-- to view indexes:
SHOW INDEX FROM recipes;
SHOW INDEX FROM users;

-- drop indexes:
-- 1. Drop Non-Clustered Index
DROP INDEX idx_recipes_prep_time ON recipes;
-- 2. Drop Unique Index
DROP INDEX idx_unique_ingredient_name ON ingredients;
-- 3. Drop Composite Index
DROP INDEX idx_difficulty_preptime ON recipes;
-- 4. Drop Full-Text Index
DROP INDEX idx_ft_recipe_search ON recipes;
-- 5. Drop Function-Based Index
DROP INDEX idx_func_lower_email ON users;
-- 6. Drop Spatial Index and remove the temporary spatial column
DROP INDEX idx_spatial_user_loc ON users;
ALTER TABLE users DROP COLUMN location;
-- 7. Drop Low-Cardinality / B-Tree Index
DROP INDEX idx_recipes_difficulty ON recipes;
-- 8. Drop Clustered Index (Primary Key) on demo table
ALTER TABLE recipe_archive DROP PRIMARY KEY;
DROP TABLE IF EXISTS recipe_archive;



-- view ---

-- Create a virtual table that shows a summary of recipes with author details:
CREATE VIEW vw_recipe_catalog AS
SELECT 
    r.recipe_id,
    r.title,
    r.prep_time,
    r.difficulty_level,
    u.username AS author
FROM recipes r
JOIN users u ON r.user_id = u.user_id;


-- view a view 
-- Query all columns from the view
SELECT * FROM vw_recipe_catalog;

-- Add custom filtering or sorting on top of the view
SELECT title, author 
FROM vw_recipe_catalog 
WHERE difficulty_level = 'Easy'
ORDER BY prep_time ASC;


-- simple view:
CREATE VIEW vw_quick_recipes AS
SELECT recipe_id, title, prep_time, servings, difficulty_level
FROM recipes
WHERE prep_time <= 30;


-- complex views :Pre-calculates recipe rating summaries and calorie profiles across 4 tables
CREATE VIEW vw_recipe_dashboard_summary AS
SELECT 
    r.recipe_id,
    r.title,
    u.username AS author,
    n.calories,
    COUNT(rv.review_id) AS total_reviews,
    ROUND(AVG(rv.rating), 2) AS average_rating
FROM recipes r
JOIN users u ON r.user_id = u.user_id
LEFT JOIN nutrition n ON r.recipe_id = n.recipe_id
LEFT JOIN reviews rv ON r.recipe_id = rv.recipe_id
GROUP BY r.recipe_id, r.title, u.username, n.calories;


--inline view: Find recipes whose calories are above the average calories calculated inside the inline view
SELECT 
    r.title, 
    n.calories, 
    stats.avg_site_calories
FROM recipes r
JOIN nutrition n ON r.recipe_id = n.recipe_id
CROSS JOIN (
    -- Inline View / Derived Table
    SELECT ROUND(AVG(calories), 2) AS avg_site_calories 
    FROM nutrition
) AS stats
WHERE n.calories > stats.avg_site_calories;


--materialized view: Emulated a materialized view using a physical snapshot table refreshed manually or via stored procedures/events
-- Step 1: Create the cached snapshot table
DROP TABLE IF EXISTS mv_recipe_performance;

CREATE TABLE mv_recipe_performance AS
SELECT 
    r.recipe_id,
    r.title,
    COUNT(rv.review_id) AS review_count,
    ROUND(AVG(rv.rating), 2) AS avg_score,
    NOW() AS last_refreshed_at
FROM recipes r
LEFT JOIN reviews rv ON r.recipe_id = rv.recipe_id
GROUP BY r.recipe_id, r.title;

-- Step 2: Query it instantly (fast read from disk cache)
SELECT * FROM mv_recipe_performance WHERE avg_score >= 4.0;
-- Step 3: Refresh procedure (simulates REFRESH MATERIALIZED VIEW)
-- TRUNCATE TABLE mv_recipe_performance;
-- INSERT INTO mv_recipe_performance ...



--  inspect view definition:
     -- Method 1: Show the complete CREATE statement
SHOW CREATE VIEW vw_recipe_catalog;

    -- Method 2: Inspect via the information_schema system catalog
SELECT table_name, view_definition 
FROM information_schema.VIEWS 
WHERE table_schema = 'recipe_portal' AND table_name = 'vw_recipe_catalog';


-- update view
     -- Using CREATE OR REPLACE VIEW:
CREATE OR REPLACE VIEW vw_recipe_catalog AS
SELECT 
    r.recipe_id,
    r.title,
    r.prep_time,
    r.servings,
    r.difficulty_level,
    u.username AS author
FROM recipes r
JOIN users u ON r.user_id = u.user_id;
-- Alternatively, using ALTER VIEW:
ALTER VIEW vw_recipe_catalog AS
SELECT 
    r.recipe_id,
    r.title,
    r.prep_time,
    r.difficulty_level,
    u.username AS author,
    u.email AS author_email
FROM recipes r
JOIN users u ON r.user_id = u.user_id;

-- drop a view:
DROP VIEW IF EXISTS vw_recipe_catalog;

-- updating data:
-- Step A: Create an updatable simple view on ingredients
CREATE OR REPLACE VIEW vw_ingredient_inventory AS
SELECT ingredient_id, name, type, cost_per_unit, stock_quantity
FROM ingredients;

-- Step B: Update stock through the view
UPDATE vw_ingredient_inventory
SET stock_quantity = stock_quantity + 10.00
WHERE ingredient_id = 1;

-- Step C: Verify that the physical 'ingredients' base table updated
SELECT ingredient_id, name, stock_quantity FROM ingredients WHERE ingredient_id = 1;

-- security:Restrict a recipe editor so they can only see and access recipes tagged as 'Easy' or authored by their specific account
CREATE VIEW vw_easy_recipes_only AS
SELECT recipe_id, title, prep_time, difficulty_level
FROM recipes
WHERE difficulty_level = 'Easy';
 

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
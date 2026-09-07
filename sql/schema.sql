DROP DATABASE IF EXISTS recipe_portal;
CREATE DATABASE recipe_portal;
USE recipe_portal;

-- 1. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('Admin', 'Chef', 'User') DEFAULT 'User',
    country VARCHAR(50) DEFAULT 'Pakistan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_email CHECK (email LIKE '%@%.%')
);

-- 2. Categories Table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL
);

-- 3. Recipes Table
CREATE TABLE recipes (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    instructions TEXT NOT NULL,
    prep_time INT NOT NULL COMMENT 'Preparation time in minutes',
    servings INT NOT NULL DEFAULT 2,
    difficulty_level ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Easy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_prep_time CHECK (prep_time > 0),
    CONSTRAINT chk_servings CHECK (servings > 0),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Recipe_Categories (Many-to-Many Bridge)
CREATE TABLE recipe_categories (
    recipe_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (recipe_id, category_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- 5. Ingredients Table (Includes Inventory & Costing)
CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NULL,
    cost_per_unit DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    stock_quantity DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_cost CHECK (cost_per_unit >= 0),
    CONSTRAINT chk_stock CHECK (stock_quantity >= 0)
);

-- 6. Recipe_Ingredients (Many-to-Many Bridge)
CREATE TABLE recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity DECIMAL(8, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    CONSTRAINT chk_ingredient_qty CHECK (quantity > 0),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE RESTRICT
);

-- 7. Nutrition Table (1-to-1 with Recipes) 
CREATE TABLE nutrition (
    nutrition_id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT UNIQUE NOT NULL,
    calories INT NOT NULL,
    protein DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    carbs DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    fats DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_calories CHECK (calories >= 0),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

-- 8. Reviews Table
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rating_range CHECK (rating BETWEEN 1 AND 5),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 9. Meal_Plans Table
CREATE TABLE meal_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    meal_date DATE NOT NULL,
    meal_type ENUM('Breakfast', 'Lunch', 'Dinner', 'Snack') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

-- 10. Audit_Logs Table (Trigger / Event Auditing)
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    table_affected VARCHAR(50) NOT NULL,
    record_id INT NULL,
    user_id INT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sample data insertion

USE recipe_portal;

-- 1. Users
INSERT INTO users (user_id, username, email, role, country) VALUES
(1, 'chef_ali', 'ali.culinary@gmail.com', 'Chef', 'Pakistan'),
(2, 'sara_bakes', 'sara.kitchen@yahoo.com', 'Chef', 'Pakistan'),
(3, 'gordon_r', 'gordon.ramsay@outlooks.com', 'Chef', 'UK'),
(4, 'foodie_zara', 'zara.food@gmail.com', 'User', 'Pakistan'),
(5, 'john_doe', 'john.d@hotmail.com', 'User', 'USA'),
(6, 'admin_master', 'admin@recipeportal.org', 'Admin', 'Pakistan');

-- 2. Categories
INSERT INTO categories (category_id, category_name, description) VALUES
(1, 'Italian', 'Authentic pastas, doughs, and Mediterranean dishes'),
(2, 'Desserts', 'Sweet pastries, cakes, and confectioneries'),
(3, 'Fast Food', 'Quick casual meals, burgers, and sides'),
(4, 'Beverages', 'Refreshing hot and cold drinks'),
(5, 'Desi Cuisine', 'Traditional spice-rich curries and rice dishes');

-- 3. Recipes
INSERT INTO recipes (recipe_id, user_id, title, instructions, prep_time, servings, difficulty_level) VALUES
(1, 1, 'Classic Margherita Pizza', 'Roll dough, spread seasoned tomato sauce, add fresh sliced mozzarella, and bake at 250C for 10 mins.', 30, 2, 'Medium'),
(2, 1, 'Spaghetti Carbonara', 'Boil pasta al dente. Whisk eggs and cheese. Toss hot pasta off heat with egg mix until creamy.', 20, 4, 'Easy'),
(3, 2, 'Molten Chocolate Lava Cake', 'Melt chocolate and butter. Whisk eggs and sugar, fold in flour, and bake at 200C for 12 mins.', 45, 2, 'Hard'),
(4, 5, 'Double Cheeseburger', 'Sear beef patties on high heat. Layer with melted cheddar, lettuce, and sauce inside brioche buns.', 25, 1, 'Easy'),
(5, 1, 'Masala Chai', 'Boil crushed cardamom, cloves, and loose tea leaves in milk and water. Simmer and strain.', 10, 2, 'Easy'),
(6, 2, 'Chicken Biryani', 'Marinate chicken in spices and yogurt. Layer parboiled basmati rice over chicken and cook on dum.', 60, 6, 'Hard'),
(7, 3, 'Tiramisu', 'Dip ladyfingers in espresso. Layer with whipped mascarpone cream and dust with cocoa powder.', 40, 6, 'Medium'),
(8, 4, 'Crispy Garlic Wedges', 'Cut potatoes into wedges, toss in olive oil and garlic herbs, and roast until golden crisp.', 35, 3, 'Easy');

-- 4. Recipe_Categories (Many-to-Many)
INSERT INTO recipe_categories (recipe_id, category_id) VALUES
(1, 1), -- Pizza -> Italian
(1, 3), -- Pizza -> Fast Food
(2, 1), -- Carbonara -> Italian
(3, 2), -- Lava Cake -> Desserts
(4, 3), -- Burger -> Fast Food
(5, 4), -- Chai -> Beverages
(6, 5), -- Biryani -> Desi Cuisine
(7, 1), -- Tiramisu -> Italian
(7, 2), -- Tiramisu -> Desserts
(8, 3); -- Wedges -> Fast Food

-- 5. Ingredients (Inventory & Pricing)
INSERT INTO ingredients (ingredient_id, name, type, cost_per_unit, stock_quantity) VALUES
(1, 'Flour', 'Baking', 120.00, 50.00),
(2, 'Mozzarella Cheese', 'Dairy', 1400.00, 15.00),
(3, 'Tomato Paste', 'Canned', 250.00, 40.00),
(4, 'Eggs', 'Dairy', 300.00, 25.00),
(5, 'Spaghetti Pasta', 'Grains', 350.00, 30.00),
(6, 'Dark Chocolate', 'Baking', 1800.00, 10.00),
(7, 'Butter', 'Dairy', 1100.00, 12.00),
(8, 'Chicken', 'Meat', 650.00, 40.00),
(9, 'Basmati Rice', 'Grains', 320.00, 60.00),
(10, 'Black Tea Leaves', 'Pantry', 450.00, 20.00),
(11, 'Milk', 'Dairy', 210.00, 35.00),
(12, 'Potatoes', 'Produce', 80.00, 100.00);

-- 6. Recipe_Ingredients (Junction Table)
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES
(1, 1, 0.40, 'kg'),     -- Pizza: Flour
(1, 2, 0.25, 'kg'),     -- Pizza: Mozzarella
(1, 3, 1.00, 'can'),    -- Pizza: Tomato Paste
(2, 5, 1.00, 'pack'),   -- Carbonara: Spaghetti
(2, 4, 0.33, 'dozen'),  -- Carbonara: Eggs
(3, 6, 0.20, 'kg'),     -- Lava Cake: Dark Chocolate
(3, 7, 0.15, 'kg'),     -- Lava Cake: Butter
(3, 4, 0.25, 'dozen'),  -- Lava Cake: Eggs
(5, 10, 0.05, 'pack'),  -- Chai: Tea Leaves
(5, 11, 0.50, 'liter'), -- Chai: Milk
(6, 8, 1.00, 'kg'),     -- Biryani: Chicken
(6, 9, 1.00, 'kg'),     -- Biryani: Rice
(8, 12, 1.00, 'kg');    -- Wedges: Potatoes

-- 7. Nutrition (1-to-1)
INSERT INTO nutrition (recipe_id, calories, protein, carbs, fats) VALUES
(1, 780, 28.50, 95.00, 32.00),
(2, 650, 24.00, 75.00, 28.00),
(3, 520, 7.00, 58.00, 30.00),
(4, 850, 42.00, 48.00, 54.00),
(5, 120, 4.00, 14.00, 5.00),
(6, 720, 35.00, 88.00, 26.00),
(7, 450, 8.00, 42.00, 28.00),
(8, 310, 5.00, 52.00, 10.00);

-- 8. Reviews
INSERT INTO reviews (recipe_id, user_id, rating, comment) VALUES
(1, 4, 5, 'The crust turned out crispy and authentic.'),
(1, 5, 4, 'Very tasty, but needed a bit more sauce.'),
(2, 5, 3, 'Creamy, but make sure not to scramble the eggs.'),
(3, 4, 5, 'The molten center came out rich and runny.'),
(6, 1, 5, 'Traditional aroma and balanced spice mix.'),
(8, 4, 4, 'Crispy on the outside, soft on the inside.');

-- 9. Meal_Plans
INSERT INTO meal_plans (user_id, recipe_id, meal_date, meal_type) VALUES
(4, 1, '2026-09-05', 'Dinner'),
(4, 5, '2026-09-06', 'Breakfast'),
(5, 2, '2026-09-05', 'Lunch'),
(5, 8, '2026-09-06', 'Snack');


CREATE DATABASE IF NOT EXISTS recipe_portal;
USE recipe_portal;
USE recipe_portal;

-- 1. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Recipes Table
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    cooking_time INT NOT NULL COMMENT 'Cooking time in minutes',
    servings INT NOT NULL,
    difficulty_level ENUM('Easy', 'Medium', 'Hard') NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- 3. Sample Seed Data
INSERT IGNORE INTO categories (category_id, category_name) VALUES
(1, 'Italian'),
(2, 'Dessert'),
(3, 'Fast Food'),
(4, 'Beverage');

INSERT IGNORE INTO recipes (recipe_id, title, cooking_time, servings, difficulty_level, category_id) VALUES
(1, 'Classic Margherita Pizza', 30, 2, 'Medium', 1),
(2, 'Spaghetti Carbonara', 20, 4, 'Easy', 1),
(3, 'Chocolate Lava Cake', 45, 2, 'Hard', 2),
(4, 'Crispy French Fries', 15, 3, 'Easy', 3),
(5, 'Iced Lemon Tea', 5, 1, 'Easy', 4);
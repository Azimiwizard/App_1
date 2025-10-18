-- Create tables for Stitch Daily Menu application
-- Run this in your Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id TEXT UNIQUE,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dishes table
CREATE TABLE IF NOT EXISTS dish (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    image_filename TEXT,
    section TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS "order" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number TEXT,
    total DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'pending',
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES "order"(id) ON DELETE CASCADE,
    dish_id UUID NOT NULL REFERENCES dish(id) ON DELETE RESTRICT,
    quantity INTEGER DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cart Items table
CREATE TABLE IF NOT EXISTS cart_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dish_id UUID NOT NULL REFERENCES dish(id) ON DELETE RESTRICT,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews table
CREATE TABLE IF NOT EXISTS review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dish_id UUID NOT NULL REFERENCES dish(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable Row Level Security for all tables (for development)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE dish DISABLE ROW LEVEL SECURITY;
ALTER TABLE "order" DISABLE ROW LEVEL SECURITY;
ALTER TABLE order_item DISABLE ROW LEVEL SECURITY;
ALTER TABLE cart_item DISABLE ROW LEVEL SECURITY;
ALTER TABLE review DISABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (for development)
CREATE POLICY "Allow all operations on users" ON users FOR ALL USING (true);
CREATE POLICY "Allow all operations on dish" ON dish FOR ALL USING (true);
CREATE POLICY "Allow all operations on order" ON "order" FOR ALL USING (true);
CREATE POLICY "Allow all operations on order_item" ON order_item FOR ALL USING (true);
CREATE POLICY "Allow all operations on cart_item" ON cart_item FOR ALL USING (true);
CREATE POLICY "Allow all operations on review" ON review FOR ALL USING (true);

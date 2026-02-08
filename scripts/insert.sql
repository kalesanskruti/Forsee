INSERT INTO organization (id, name, created_at, updated_at) 
VALUES ('f6ca64e5-5c1c-4b1a-8b1a-1a2b3c4d5e6f', 'Main Org', now(), now()) 
ON CONFLICT DO NOTHING;

INSERT INTO "user" (id, email, hashed_password, full_name, role, org_id, is_active, created_at, updated_at)
VALUES (
    'a3b8d1b6-0b3b-4b1a-9c1a-1a2b3c4d5e6f', 
    'admin@forsee.ai', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGGa31S.', 
    'System Admin', 
    'ADMIN', 
    'f6ca64e5-5c1c-4b1a-8b1a-1a2b3c4d5e6f', 
    true, 
    now(), 
    now()
)
ON CONFLICT (email) DO NOTHING;

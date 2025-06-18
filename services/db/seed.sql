INSERT INTO tenant (id, name, plan, created_at)
VALUES (1, 'admin', 'enterprise', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO "user" (id, tenant_id, email, password_hash, role, is_active, created_at)
VALUES (
    1,
    1,
    'admin@smartsecurity.solutions',
    '$2b$12$KIX8Wc1xi9HQhIOrH6W1C.jvdO1rRdtqvYX0fOkH3Wv4EvsC0.1Ca',
    'admin',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT DO NOTHING;

from core import security
import psycopg2
import uuid

# Production/Docker DB URL: 
# Since this runs inside Docker or Host? 
# I want to run it inside Docker.
DB_URL = "postgresql://postgres:securepassword@db:5432/forsee"

def create_user():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        email = "admin@forsee.ai"
        password = "password123"
        hashed = security.get_password_hash(password)
        
        # 1. Get or Create Org
        cur.execute("SELECT id FROM organization WHERE name = 'Main Org'")
        row = cur.fetchone()
        if not row:
            org_id = str(uuid.uuid4())
            cur.execute("INSERT INTO organization (id, name, created_at, updated_at) VALUES (%s, %s, now(), now())", (org_id, "Main Org"))
            print(f"Created Org: {org_id}")
        else:
            org_id = row[0]
            print(f"Using Org: {org_id}")
            
        # 2. Delete existing user if any to reset cleanly
        cur.execute("DELETE FROM \"user\" WHERE email = %s", (email,))
        
        # 3. Insert user
        user_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO \"user\" (id, email, hashed_password, full_name, role, org_id, is_active, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, true, now(), now())",
            (user_id, email, hashed, "System Admin", "ADMIN", org_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"SUCCESS: User {email} created with password {password}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_user()

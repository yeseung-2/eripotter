import psycopg2

# Railway PostgreSQL 연결
conn = psycopg2.connect(
    "postgresql://postgres:liyjJKKLWfrWOMFvdgPsWpJvcFdBUsks@switchyard.proxy.rlwy.net:38891/railway"
)
cursor = conn.cursor()

# SQL 파일 읽기
with open('create_sharing_tables.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# SQL 실행
print("🔧 SQL 실행 중...")
cursor.execute(sql)
conn.commit()

print("✅ 완료!")
cursor.close()
conn.close()

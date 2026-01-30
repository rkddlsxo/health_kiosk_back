"""
kiosk 데이터베이스 생성 스크립트
"""
import pymysql

print("MySQL에 kiosk 데이터베이스 생성 중...")

try:
    # MySQL root 연결 (데이터베이스 지정 안 함)
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1234'
    )
    
    cursor = connection.cursor()
    
    # 데이터베이스 생성
    cursor.execute("CREATE DATABASE IF NOT EXISTS kiosk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("✅ kiosk 데이터베이스 생성 완료!")
    
    # 확인
    cursor.execute("SHOW DATABASES")
    databases = [row[0] for row in cursor.fetchall()]
    if 'kiosk' in databases:
        print(f"✅ kiosk 데이터베이스 확인됨")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ 오류: {e}")
    exit(1)

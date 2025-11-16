from database import engine, create_tables, SessionLocal
from models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

def test_database():
    print("🧪 Testing database setup...")
    
    # 1. Create tables
    create_tables()
    print("✅ Tables created")
    
    # 2. Test connection
    with SessionLocal() as session:
        result = session.execute(text("SELECT version();"))
        print(f"✅ PostgreSQL: {result.fetchone()[0]}")
        
        # 3. Test table exists
        result = session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'transactions';"))
        table_exists = result.scalar() > 0
        print(f"✅ Transactions table exists: {table_exists}")
        
        # 4. Test insert
        test_id = str(uuid.uuid4())
        transaction = Transaction(
            momo_reference_id=test_id,
            external_id="test-456",
            amount=25.50,
            currency="GHS",
            payer_phone_number="233500000001",
            status="SUCCESSFUL",
            payer_message="Final test",
            payee_note="Test completed"
        )
        session.add(transaction)
        session.commit()
        print("✅ Transaction inserted")
        
        # 5. Test read
        saved = session.query(Transaction).filter_by(momo_reference_id=test_id).first()
        print(f"✅ Transaction retrieved: {saved.amount} {saved.currency}")
        
        # 6. Test delete
        session.delete(saved)
        session.commit()
        print("✅ Transaction deleted")
        
        # 7. Final count
        count = session.execute(text("SELECT COUNT(*) FROM transactions;")).scalar()
        print(f"✅ Final transaction count: {count}")

if __name__ == "__main__":
    test_database()
    print("\n🎉 ALL DATABASE TESTS PASSED! Your system is ready for payments.")
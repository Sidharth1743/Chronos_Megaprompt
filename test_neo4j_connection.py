#!/usr/bin/env python3
"""
Quick test script to verify Neo4j Aura connection
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

def test_neo4j_connection():
    """Test Neo4j Aura connection"""

    NEO4J_URL = os.environ.get("NEO4J_URL")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

    print("\n" + "="*80)
    print("🧪 TESTING NEO4J AURA CONNECTION")
    print("="*80)
    print(f"\n📍 URL: {NEO4J_URL}")
    print(f"👤 Username: {NEO4J_USERNAME}")
    print(f"🔐 Password: {'*' * len(NEO4J_PASSWORD)}")
    print()

    try:
        # Create driver
        print("🔌 Connecting to Neo4j Aura...")
        driver = GraphDatabase.driver(
            NEO4J_URL,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )

        # Verify connectivity
        print("✓ Driver created")

        driver.verify_connectivity()
        print("✓ Connectivity verified")

        # Test query
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            value = result.single()["test"]
            print(f"✓ Test query successful (returned: {value})")

        # Get server info
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            record = result.single()
            print(f"\n📊 Neo4j Server Info:")
            print(f"   Name: {record['name']}")
            print(f"   Version: {record['versions'][0]}")
            print(f"   Edition: {record['edition']}")

        # Count existing nodes
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"\n📈 Current Database:")
            print(f"   Nodes: {count}")

        driver.close()

        print("\n" + "="*80)
        print("✅ CONNECTION TEST SUCCESSFUL!")
        print("="*80)
        print("\nYour Neo4j Aura instance is ready to use!")
        print("You can now deploy to Render with these credentials.")
        return True

    except Exception as e:
        print("\n" + "="*80)
        print("❌ CONNECTION TEST FAILED")
        print("="*80)
        print(f"\nError: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Neo4j Aura instance is running (green status)")
        print("2. Verify the URL starts with 'neo4j+s://'")
        print("3. Confirm username and password are correct")
        print("4. Check Network Access settings in Aura Console")
        return False


if __name__ == "__main__":
    test_neo4j_connection()

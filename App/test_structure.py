#!/usr/bin/env python3
"""Test script to verify MVC structure"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing MVC structure...")

try:
    print("\n1. Testing models import...")
    from models import FileProcessor, AlgorithmComparator, DatabaseManager
    print("   ✓ Models imported successfully")
except Exception as e:
    print(f"   ✗ Error importing models: {e}")
    sys.exit(1)

try:
    print("\n2. Testing controllers import...")
    from controllers import MainController
    print("   ✓ Controllers imported successfully")
except Exception as e:
    print(f"   ✗ Error importing controllers: {e}")
    sys.exit(1)

try:
    print("\n3. Testing views import...")
    from views import LoginView, MainView
    print("   ✓ Views imported successfully")
except Exception as e:
    print(f"   ✗ Error importing views: {e}")
    sys.exit(1)

try:
    print("\n4. Testing main module...")
    import main
    print("   ✓ Main module imported successfully")
except Exception as e:
    print(f"   ✗ Error importing main: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✓ All MVC components verified successfully!")
print("="*50)
print("\nProject structure:")
print("  models/")
print("    - FileProcessor")
print("    - RabinKarpSearch, SuffixTreeSearch, SemanticSearch")
print("    - AlgorithmComparator")
print("    - DatabaseManager")
print("\n  controllers/")
print("    - MainController")
print("\n  views/")
print("    - LoginView")
print("    - MainView")
print("\n  main.py - Entry point")

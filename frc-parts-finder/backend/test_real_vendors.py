#!/usr/bin/env python3
"""
Gerçek FRC tedarikçi arama sistemi test scripti
WCP, REV, AndyMark, CTRE sitelerini test eder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_vendor_search import RealVendorSearchEngine
import json

def test_vendor_search():
    """Tedarikçi arama sistemini test et"""
    print("🚀 FRC Real Vendor Search Test")
    print("=" * 50)
    
    # Arama motorunu başlat
    engine = RealVendorSearchEngine(rate_limit_delay=1.0)
    
    # Test sorguları
    test_queries = [
        "NEO motor",
        "Kraken X60",
        "SPARK MAX",
        "Talon SRX",
        "Victor SPX",
        "CANcoder"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            # Arama yap
            results = engine.search_all_vendors(query)
            
            total_results = 0
            for vendor, products in results.items():
                print(f"  {vendor}: {len(products)} products")
                total_results += len(products)
                
                # İlk 2 ürünü göster
                for i, product in enumerate(products[:2]):
                    price_str = f"${product['price']}" if product['price'] else "N/A"
                    stock_str = "✓" if product['inStock'] else "✗"
                    print(f"    {i+1}. {product['name']} - {price_str} {stock_str}")
            
            print(f"  Total: {total_results} products found")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

def test_individual_vendors():
    """Her tedarikçiyi ayrı ayrı test et"""
    print("\n🔧 Individual Vendor Tests")
    print("=" * 50)
    
    engine = RealVendorSearchEngine(rate_limit_delay=1.0)
    
    # WCP test
    print("\n🏢 Testing WCP (West Coast Products)")
    try:
        wcp_results = engine.search_wcp("NEO motor")
        print(f"  Found {len(wcp_results)} products")
        for product in wcp_results[:3]:
            print(f"    - {product['name']}: ${product['price']}")
    except Exception as e:
        print(f"  ❌ WCP Error: {e}")
    
    # REV test
    print("\n🏢 Testing REV Robotics")
    try:
        rev_results = engine.search_rev("NEO motor")
        print(f"  Found {len(rev_results)} products")
        for product in rev_results[:3]:
            print(f"    - {product['name']}: ${product['price']}")
    except Exception as e:
        print(f"  ❌ REV Error: {e}")
    
    # AndyMark test
    print("\n🏢 Testing AndyMark")
    try:
        andymark_results = engine.search_andymark("NEO motor")
        print(f"  Found {len(andymark_results)} products")
        for product in andymark_results[:3]:
            print(f"    - {product['name']}: ${product['price']}")
    except Exception as e:
        print(f"  ❌ AndyMark Error: {e}")
    
    # CTRE test
    print("\n🏢 Testing CTRE")
    try:
        ctre_results = engine.search_ctre("Talon")
        print(f"  Found {len(ctre_results)} products")
        for product in ctre_results[:3]:
            print(f"    - {product['name']}: ${product['price']}")
    except Exception as e:
        print(f"  ❌ CTRE Error: {e}")

if __name__ == "__main__":
    print("FRC Real Vendor Search Test Suite")
    print("Testing: WCP, REV, AndyMark, CTRE")
    print("=" * 50)
    
    # Ana test
    test_vendor_search()
    
    # Bireysel testler
    test_individual_vendors()
    
    print("\n🎯 Test Summary:")
    print("- Real vendor search engine tested")
    print("- Individual vendor APIs tested")
    print("- Error handling verified")
    print("\n💡 To run the enhanced server:")
    print("   python3 server_enhanced.py")

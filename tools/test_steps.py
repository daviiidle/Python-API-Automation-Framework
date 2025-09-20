#!/usr/bin/env python3
"""
Test script to debug Behave step discovery issues.
"""
import sys
import os
sys.path.append('.')

def test_step_discovery():
    """Test if all steps can be discovered properly."""
    
    # Import behave components
    try:
        from behave import step_registry
        from behave.step_registry import StepRegistry
        
        print("✅ Behave imports successful")
        
        # Create a test registry
        registry = StepRegistry()
        
        # Import step modules to register steps
        from features.steps import common_steps
        from features.steps import auth_steps  
        from features.steps import data_steps
        
        print("✅ Step modules imported")
        
        # Check what steps are registered
        print(f"📊 Steps registered in registry: {len(registry.steps)}")
        
        # Test specific step patterns
        test_patterns = [
            "Given the banking API is available",
            "And I have valid authentication credentials", 
            "When I send a POST request to \"/accounts\" with data:",
            "Then the response status code should be 201",
            "And the response should contain \"accountId\"",
            "Then I should receive an unauthorized error"
        ]
        
        for pattern in test_patterns:
            try:
                step_def = registry.find_step_definition(pattern)
                if step_def:
                    print(f"✅ Found: {pattern}")
                else:
                    print(f"❌ Missing: {pattern}")
            except Exception as e:
                print(f"❌ Error finding: {pattern} - {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_step_discovery()

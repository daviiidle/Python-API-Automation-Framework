"""
Data-driven step definitions for Banking API BDD tests.
Handles dynamic data generation and table-based test scenarios.
"""

import json
from typing import Dict, Any

from behave import given, when, then, step
from behave.runner import Context

from support.utils.data_generator import data_generator


# ============================================================================
# Data Generation Steps
# ============================================================================

@given('I generate test data for "{data_type}"')
def step_generate_test_data(context: Context, data_type: str):
    """Generate test data for specified type."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    if data_type == 'customer':
        context.test_data['customer'] = data_generator.generate_customer_data()
    elif data_type == 'account':
        context.test_data['account'] = data_generator.generate_account_data()
    elif data_type == 'booking':
        context.test_data['booking'] = data_generator.generate_booking_data()
    elif data_type == 'loan':
        context.test_data['loan'] = data_generator.generate_loan_data()
    elif data_type == 'term_deposit':
        context.test_data['term_deposit'] = data_generator.generate_term_deposit_data()
    else:
        raise ValueError(f"Unknown data type: {data_type}")


@given('I generate {count:d} test records for "{data_type}"')
def step_generate_multiple_test_data(context: Context, count: int, data_type: str):
    """Generate multiple test records for load testing."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    context.test_data[f'{data_type}_list'] = data_generator.generate_multiple_records(data_type, count)


@given('I generate invalid data for "{data_type}" with invalid "{field}"')
def step_generate_invalid_data(context: Context, data_type: str, field: str):
    """Generate invalid test data for negative testing."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    context.test_data[f'invalid_{data_type}'] = data_generator.generate_invalid_data(data_type, field)


@given('I generate boundary data for "{data_type}" with "{boundary_type}" values')
def step_generate_boundary_data(context: Context, data_type: str, boundary_type: str):
    """Generate boundary condition test data."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    context.test_data[f'boundary_{data_type}'] = data_generator.generate_boundary_data(data_type, boundary_type)


@when('I create a "{data_type}" using generated data')
def step_create_using_generated_data(context: Context, data_type: str):
    """Create resource using previously generated test data."""
    if not hasattr(context, 'test_data') or data_type not in context.test_data:
        raise ValueError(f"No test data generated for {data_type}")
    
    data = context.test_data[data_type]
    
    # Map data types to endpoints
    endpoints = {
        'customer': '/customers',
        'account': '/accounts',
        'booking': '/bookings',
        'loan': '/loans',
        'term_deposit': '/term-deposits'
    }
    
    if data_type in endpoints:
        context.api_client.post(endpoints[data_type], json_data=data)


@when('I retrieve the created "{data_type}" using generated ID')
def step_retrieve_using_generated_id(context: Context, data_type: str):
    """Retrieve resource using ID from generated test data."""
    if not hasattr(context, 'test_data'):
        raise ValueError("No test data available")
    
    # Get the ID from the last response or test data
    last_response = context.api_client.get_last_response_json()
    if last_response:
        id_field = f"{data_type}Id"
        if id_field in last_response:
            resource_id = last_response[id_field]
            
            # Map data types to endpoints
            endpoints = {
                'customer': f'/customers/{resource_id}',
                'account': f'/accounts/{resource_id}',
                'booking': f'/bookings/{resource_id}',
                'loan': f'/loans/{resource_id}',
                'term_deposit': f'/term-deposits/{resource_id}'
            }
            
            if data_type in endpoints:
                context.api_client.get(endpoints[data_type])


# ============================================================================
# Table-Driven Test Steps
# ============================================================================

@when('I create accounts with the following data')
def step_create_accounts_from_table(context: Context):
    """Create accounts using data from Behave table."""
    if not context.table:
        raise ValueError("No table data provided")
    
    results = []
    for row in context.table:
        # Generate base data and override with table values
        account_data = data_generator.generate_account_data()
        
        # Override with table values
        for heading in context.table.headings:
            if row[heading] and row[heading].lower() not in ['null', 'none', '']:
                # Convert string values to appropriate types
                value = row[heading]
                if heading in ['initialBalance', 'amount']:
                    value = float(value) if '.' in value else int(value)
                elif heading in ['active']:
                    value = value.lower() == 'true'
                
                account_data[heading] = value
        
        # Make API call
        response = context.api_client.post('/accounts', json_data=account_data)
        results.append({
            'data': account_data,
            'response': response,
            'status_code': response.status_code
        })
    
    context.batch_results = results


@when('I test customer creation with various scenarios')
def step_test_customer_scenarios_table(context: Context):
    """Test customer creation with table-driven scenarios."""
    if not context.table:
        raise ValueError("No table data provided")
    
    results = []
    for row in context.table:
        scenario = row['scenario']
        
        # Generate data based on scenario
        if scenario == 'valid_data':
            customer_data = data_generator.generate_customer_data()
        elif scenario == 'invalid_email':
            customer_data = data_generator.generate_invalid_data('customer', 'email')
        elif scenario == 'missing_phone':
            customer_data = data_generator.generate_customer_data()
            del customer_data['phone']
        elif scenario == 'boundary_min':
            customer_data = data_generator.generate_boundary_data('customer', 'min')
        elif scenario == 'boundary_max':
            customer_data = data_generator.generate_boundary_data('customer', 'max')
        else:
            customer_data = data_generator.generate_customer_data()
        
        response = context.api_client.post('/customers', json_data=customer_data)
        results.append({
            'scenario': scenario,
            'expected_status': int(row['expected_status']),
            'actual_status': response.status_code,
            'data': customer_data
        })
    
    context.scenario_results = results


@then('all account creations should have the expected results')
def step_verify_batch_account_results(context: Context):
    """Verify results from batch account creation."""
    if not hasattr(context, 'batch_results'):
        raise ValueError("No batch results available")
    
    for result in context.batch_results:
        expected_status = 201 if 'invalid' not in str(result['data']) else 400
        assert result['status_code'] == expected_status, \
            f"Expected {expected_status}, got {result['status_code']} for data: {result['data']}"


@then('all scenario results should match expectations')
def step_verify_scenario_results(context: Context):
    """Verify results from scenario-driven tests."""
    if not hasattr(context, 'scenario_results'):
        raise ValueError("No scenario results available")
    
    for result in context.scenario_results:
        assert result['actual_status'] == result['expected_status'], \
            f"Scenario '{result['scenario']}': Expected {result['expected_status']}, got {result['actual_status']}"


# ============================================================================
# Data Validation Steps
# ============================================================================

@then('the response should contain generated "{field}" value')
def step_verify_generated_field(context: Context, field: str):
    """Verify that response contains the value from generated test data."""
    if not hasattr(context, 'test_data'):
        raise ValueError("No test data available for verification")
    
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response is not valid JSON"
    
    # Find the field in test data
    generated_value = None
    for data_type, data in context.test_data.items():
        if isinstance(data, dict) and field in data:
            generated_value = data[field]
            break
    
    assert generated_value is not None, f"Field '{field}' not found in generated test data"
    assert field in response_json, f"Field '{field}' not found in response"
    assert response_json[field] == generated_value, \
        f"Expected {generated_value}, got {response_json[field]}"


@then('the generated data should be realistic and valid')
def step_verify_data_realism(context: Context):
    """Verify that generated data follows realistic patterns."""
    if not hasattr(context, 'test_data'):
        raise ValueError("No test data available for verification")
    
    for data_type, data in context.test_data.items():
        if isinstance(data, dict):
            # Verify email format
            if 'email' in data:
                assert '@' in data['email'], f"Invalid email format: {data['email']}"
            
            # Verify phone format
            if 'phone' in data:
                assert data['phone'].startswith('+'), f"Invalid phone format: {data['phone']}"
            
            # Verify positive amounts
            if 'amount' in data or 'initialBalance' in data:
                amount = data.get('amount') or data.get('initialBalance')
                assert amount >= 0, f"Amount should be non-negative: {amount}"
            
            # Verify date formats
            if 'dob' in data:
                assert len(data['dob']) == 10, f"Invalid date format: {data['dob']}"


@step('I save the generated correlation ID')
def step_save_correlation_id(context: Context):
    """Generate and save correlation ID for tracking."""
    correlation_id = data_generator.generate_correlation_id()
    context.api_client.set_correlation_id(correlation_id)
    
    if not hasattr(context, 'saved_data'):
        context.saved_data = {}
    context.saved_data['correlation_id'] = correlation_id


@step('I generate performance test dataset with {count:d} records')
def step_generate_performance_dataset(context: Context, count: int):
    """Generate large dataset for performance testing."""
    context.performance_data = data_generator.generate_performance_test_data(count)


@when('I create multiple resources using performance dataset')
def step_create_multiple_resources(context: Context):
    """Create multiple resources for performance testing."""
    if not hasattr(context, 'performance_data'):
        raise ValueError("No performance dataset available")
    
    import concurrent.futures
    import time
    
    def create_customer(data_item):
        """Create a customer record."""
        start_time = time.time()
        response = context.api_client.post('/customers', json_data=data_item['customer'])
        end_time = time.time()
        return {
            'status_code': response.status_code,
            'response_time': end_time - start_time,
            'correlation_id': data_item['correlation_id']
        }
    
    start_time = time.time()
    
    # Execute requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_customer, item) for item in context.performance_data[:10]]  # Limit to 10 for demo
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    context.performance_results = {
        'results': results,
        'total_time': total_time,
        'requests_per_second': len(results) / total_time
    }


@then('the performance should meet the required thresholds')
def step_verify_performance_thresholds(context: Context):
    """Verify performance meets required thresholds."""
    if not hasattr(context, 'performance_results'):
        raise ValueError("No performance results available")
    
    results = context.performance_results['results']
    
    # Verify all requests succeeded
    success_count = sum(1 for r in results if 200 <= r['status_code'] < 300)
    success_rate = success_count / len(results)
    assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"
    
    # Verify average response time
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    assert avg_response_time <= 3.0, f"Average response time too high: {avg_response_time:.3f}s"
    
    # Verify requests per second
    rps = context.performance_results['requests_per_second']
    assert rps >= 1.0, f"Requests per second too low: {rps:.2f}"
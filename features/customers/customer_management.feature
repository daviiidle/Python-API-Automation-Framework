@api @banking @customers @regression @dynamic_data
Feature: Customer Management
  As a banking API client
  I want to manage customer information
  So that I can maintain accurate customer records

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create customer with generated data
    Given I generate test data for "customer"
    When I create a "customer" using generated data
    Then the response status code should be 201
    And the response should be valid JSON
    And the response should contain "customerId"
    And the response should contain "firstName"
    And the response should contain "lastName"
    And the response should contain "email"
    And the response should contain "phone"
    And the response should contain "createdAt"

  @happy_path @smoke
  Scenario: Successfully retrieve customer with generated ID
    Given I generate test data for "customer"
    When I create a "customer" using generated data
    Then the response status code should be 201
    When I retrieve the created "customer" using generated ID
    Then the response status code should be 200
    And the response should contain "customerId"

  @table_driven @regression
  Scenario: Test customer creation with various scenarios
    When I test customer creation with various scenarios:
      | scenario      | expected_status |
      | valid_data    | 201            |
      | invalid_email | 400            |
      | missing_phone | 400            |
      | boundary_min  | 201            |
      | boundary_max  | 201            |
    Then all scenario results should match expectations

  @error_handling @regression
  Scenario: Customer retrieval without authentication
    Given I have no authentication token
    When I send a GET request to "/customers/CUST001"
    Then I should receive an unauthorized error
    Then I restore the original authentication

  @performance @load_testing
  Scenario: Create multiple customers for performance testing
    Given I generate performance test dataset with 10 records
    When I create multiple resources using performance dataset
    Then the performance should meet the required thresholds

  @data_validation @regression  
  Scenario: Verify customer data format and types
    Given I generate test data for "customer"
    When I create a "customer" using generated data
    Then the response status code should be 201
    And the generated data should be realistic and valid
    And the response should contain generated "firstName" value
    And the response should contain generated "lastName" value
    And the response should contain generated "email" value
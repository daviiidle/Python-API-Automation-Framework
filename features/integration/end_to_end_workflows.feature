@api @banking @integration @end_to_end @regression
Feature: End-to-End Banking Workflows
  As a banking API client
  I want to perform complete banking workflows
  So that I can simulate real customer journeys

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @workflow @smoke @quarantine
  Scenario: Complete customer onboarding workflow
    Given I generate test data for "customer"
    And I save the generated correlation ID
    When I create a "customer" using generated data
    Then the response status code should be 201
    And I save the response "customerId" as "customer_id"
    
    Given I generate test data for "account"
    When I create a "account" using generated data
    Then the response status code should be 201
    And I save the response "accountId" as "account_id"
    
    When I send a GET request to "/customers/{customer_id}" with substitution
    Then the response status code should be 200
    When I send a GET request to "/accounts/{account_id}" with substitution
    Then the response status code should be 200

  @workflow @regression
  Scenario: Customer service booking workflow
    Given I generate test data for "customer"
    When I create a "customer" using generated data
    Then the response status code should be 201
    
    Given I generate test data for "booking"
    When I create a "booking" using generated data
    Then the response status code should be 201
    
    When I retrieve the created "booking" using generated ID
    Then the response status code should be 200

  @workflow @regression
  Scenario: Loan application workflow
    Given I generate test data for "customer"
    When I create a "customer" using generated data
    Then the response status code should be 201
    
    Given I generate test data for "loan"
    When I create a "loan" using generated data
    Then the response status code should be 201
    
    When I retrieve the created "loan" using generated ID
    Then the response status code should be 200

  @performance @load_testing @workflow
  Scenario: Performance testing with multiple workflows
    Given I generate performance test dataset with 5 records
    When I create multiple resources using performance dataset
    Then the performance should meet the required thresholds
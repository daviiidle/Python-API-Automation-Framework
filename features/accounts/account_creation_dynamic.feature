@api @banking @accounts @regression @dynamic_data
Feature: Account Creation with Dynamic Data
  As a banking API client
  I want to create accounts using dynamic test data
  So that I can test with realistic and varied data scenarios

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create account with generated data
    Given I generate test data for "account"
    When I create a "account" using generated data
    Then the response status code should be 201
    And the response should be valid JSON
    And the response should contain "accountId"
    And the response should contain "customerId"
    And the response should contain "accountType"
    And the response should contain "currency"
    And the response should contain "createdAt"
    And the generated data should be realistic and valid

  @table_driven @regression
  Scenario: Create accounts with various account types and currencies
    When I create accounts with the following data:
      | accountType   | currency | initialBalance | description           |
      | SAVINGS       | AUD      | 1000.50       | Primary savings       |
      | CHECKING      | USD      | 2500.00       | USD checking account  |
      | TERM_DEPOSIT  | EUR      | 10000.00      | Euro term deposit     |
      | CREDIT_CARD   | GBP      | 0.00          | GBP credit card       |
      | SAVINGS       | AUD      | 0.01          | Minimum balance test  |
    Then all account creations should have the expected results

  @boundary_testing @regression
  Scenario Outline: Create accounts with boundary values
    Given I generate boundary data for "account" with "<boundary_type>" values
    When I create a "account" using generated data
    Then the response status code should be <expected_status>

    Examples:
      | boundary_type | expected_status |
      | min           | 201             |
      | max           | 201             |

  @negative_testing @error_handling
  Scenario Outline: Attempt to create accounts with invalid data
    Given I generate invalid data for "account" with invalid "<invalid_field>"
    When I create a "account" using generated data
    Then the response status code should be 400
    And the response should contain an error message

    Examples:
      | invalid_field    |
      | customerId       |
      | initialBalance   |
      | accountType      |

  @performance @load_testing
  Scenario: Create multiple accounts for performance testing
    Given I generate 5 test records for "account"
    When I create multiple resources using performance dataset
    Then the performance should meet the required thresholds

  @data_validation @regression
  Scenario: Verify account creation response contains generated data
    Given I generate test data for "account"
    When I create a "account" using generated data
    Then the response status code should be 201
    And the response should contain generated "customerId" value
    And the response should contain generated "accountType" value
    And the response should contain generated "currency" value

  @correlation_tracking
  Scenario: Create account with generated correlation ID
    Given I save the generated correlation ID
    And I generate test data for "account"
    When I create a "account" using generated data
    Then the response status code should be 201
    And the response should contain the correlation ID

  @concurrent_creation
  Scenario: Create multiple accounts concurrently
    Given I generate 3 test records for "account"
    When I create multiple resources using performance dataset
    Then the performance should meet the required thresholds
    And all scenario results should match expectations

  @realistic_data_testing
  Scenario: Verify generated account data is realistic
    Given I generate test data for "account"
    Then the generated data should be realistic and valid
    When I create a "account" using generated data
    Then the response status code should be 201

  @currency_variety_testing
  Scenario: Create accounts with different currencies using table
    When I create accounts with the following data:
      | currency | accountType | initialBalance |
      | AUD      | SAVINGS     | 1500.75       |
      | USD      | CHECKING    | 3200.00       |
      | EUR      | SAVINGS     | 2100.25       |
      | GBP      | TERM_DEPOSIT| 8500.00       |
      | CAD      | CHECKING    | 1800.50       |
    Then all account creations should have the expected results
@api @banking @accounts @regression
Feature: Account Creation
  As a banking API client
  I want to create new accounts
  So that I can establish customer accounts in the system

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create account with valid generated data
    Given I generate test data for "account"
    When I create a "account" using generated data
    Then the response status code should be 201
    And the response should be valid JSON
    And the response should contain "accountId"
    And the response should contain "customerId"
    And the response should contain "accountType"
    And the response should contain "currency"
    And the response should contain "createdAt"
    And the response should contain the correlation ID

  @happy_path @regression
  Scenario: Create account with minimum required fields
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST002",
        "accountType": "CHECKING",
        "currency": "AUD"
      }
      """
    Then the response status code should be 201
    And the response should contain "accountId"
    And the response "customerId" should be "CUST002"
    And the response "accountType" should be "CHECKING"

  @data_validation @regression
  Scenario: Create account with all optional fields
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST003",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 5000.00,
        "description": "Primary savings account",
        "branch": "Melbourne CBD"
      }
      """
    Then the response status code should be 201
    And the response should contain "accountId"
    And the response should contain "description"
    And the response should contain "branch"

  @error_handling @regression
  Scenario: Attempt to create account without authentication
    Given I have no authentication token
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then I should receive an unauthorized error
    And the error message should indicate missing authorization
    Then I restore the original authentication

  @error_handling @regression
  Scenario: Attempt to create account with missing required fields
    When I send a POST request to "/accounts" with data:
      """
      {
        "accountType": "SAVINGS"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @error_handling @regression
  Scenario: Attempt to create account with invalid customer ID
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @error_handling @regression
  Scenario: Attempt to create account with invalid account type
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "INVALID_TYPE",
        "currency": "AUD"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @boundary_testing
  Scenario Outline: Create account with boundary values
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "<customer_id>",
        "accountType": "<account_type>",
        "currency": "<currency>",
        "initialBalance": <balance>
      }
      """
    Then the response status code should be <expected_status>

    Examples:
      | customer_id | account_type | currency | balance | expected_status |
      | CUST001    | SAVINGS      | AUD      | 0.00    | 201             |
      | CUST001    | SAVINGS      | AUD      | -100.00 | 400             |
      | CUST001    | SAVINGS      | AUD      | 999999  | 201             |
      | VERYLONGCUSTOMERID123456789 | SAVINGS | AUD   | 1000    | 400             |

  @data_types_validation
  Scenario: Attempt to create account with invalid data types
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": 123,
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": "invalid_number"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @currency_validation
  Scenario Outline: Create accounts with different currencies
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "<currency>",
        "initialBalance": 1000.00
      }
      """
    Then the response status code should be <expected_status>

    Examples:
      | currency | expected_status |
      | AUD      | 201             |
      | USD      | 201             |
      | EUR      | 201             |
      | GBP      | 201             |
      | XXX      | 400             |
      | invalid  | 400             |

  @duplicate_handling
  Scenario: Attempt to create duplicate account for same customer
    Given I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
      }
      """
    And the response status code should be 201
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
      }
      """
    Then the response status code should be 409
    And the response should contain an error message

  @performance
  Scenario: Account creation performance validation
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
      }
      """
    Then the response status code should be 201
    And the response time should be under 3000 milliseconds

  @schema_validation
  Scenario: Verify account creation response schema
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
      }
      """
    Then the response status code should be 201
    And the response should match the schema
    And the response should contain the following fields:
      | field          |
      | accountId      |
      | customerId     |
      | accountType    |
      | currency       |
      | initialBalance |
      | createdAt      |

  @special_characters
  Scenario: Create account with special characters in description
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00,
        "description": "Savings account with émojis 💰 and special chars !@#$%"
      }
      """
    Then the response status code should be 201
    And the response should contain "description"

  @content_type_validation
  Scenario: Attempt to create account with incorrect content type
    Given I set the "Content-Type" header to "text/plain"
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message
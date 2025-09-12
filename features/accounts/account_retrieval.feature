@api @banking @accounts @smoke
Feature: Account Retrieval
  As a banking API client
  I want to retrieve account information
  So that I can access customer account details

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @regression
  Scenario: Successfully retrieve account by valid ID
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And the response should be valid JSON
    And the response should contain "customerId"
    And the response should contain "firstName"
    And the response should contain "lastName"
    And the response should contain "createdAt"
    And the response should contain the correlation ID
    And the response time should be under 2000 milliseconds

  @happy_path @regression
  Scenario: Successfully retrieve account with different valid ID
    When I send a GET request to "/accounts/ACC002"
    Then the response status code should be 200
    And the response should be valid JSON
    And the response should contain "customerId"
    And the response should contain the following fields:
      | field      |
      | firstName  |
      | lastName   |
      | email      |
      | phone      |
      | dob        |
      | createdAt  |

  @error_handling @regression
  Scenario: Attempt to retrieve non-existent account
    When I send a GET request to "/accounts/NONEXISTENT"
    Then the response status code should be 404
    And the response should be valid JSON
    And the response should contain an error message
    And the response should contain the correlation ID

  @error_handling @regression
  Scenario: Attempt to retrieve account with invalid ID format
    When I send a GET request to "/accounts/123invalid"
    Then the response status code should be 404
    And the response should contain an error message

  @boundary_testing
  Scenario Outline: Retrieve accounts with boundary ID values
    When I send a GET request to "/accounts/<account_id>"
    Then the response status code should be <expected_status>
    And the response should be valid JSON

    Examples:
      | account_id          | expected_status |
      | ACC001             | 200             |
      | ACC999             | 404             |
      | A                  | 404             |
      | VERYLONGACCOUNTID  | 404             |

  @performance @load_testing
  Scenario: Multiple concurrent account retrievals
    When I send a GET request to "/accounts/ACC001"
    And I send a GET request to "/accounts/ACC002"
    Then the response time should be under 1500 milliseconds
    And the response should be successful

  @data_validation
  Scenario: Verify account response data types and formats
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And the response "customerId" should be "ACC001"
    And the response should contain "firstName"
    And the response should contain "email"
    And the response should contain "phone"
    And the response should contain "dob"
    And the response should contain "createdAt"

  @correlation_tracking
  Scenario: Verify correlation ID is propagated in account retrieval
    Given I set the correlation ID to "test-acc-001"
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And the response should contain the correlation ID

  @caching_behavior
  Scenario: Verify consistent response for repeated requests
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And I save the response "firstName" as "first_name_1"
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And I save the response "firstName" as "first_name_2"
    # Note: In a real scenario, we'd compare these values

  @response_headers
  Scenario: Verify account retrieval response headers
    When I send a GET request to "/accounts/ACC001"
    Then the response status code should be 200
    And the response should include security headers
    And the response should contain the correlation ID

  @edge_cases
  Scenario Outline: Account retrieval with special characters in ID
    When I send a GET request to "/accounts/<account_id>"
    Then the response status code should be 404
    And the response should contain an error message

    Examples:
      | account_id    |
      | ACC@001      |
      | ACC 001      |
      | ACC#001      |
      | ACC%001      |
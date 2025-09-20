@api @banking @accounts @error_handling
Feature: Account Error Handling
  As a banking API client
  I want to receive appropriate error responses for invalid account operations
  So that I can handle errors gracefully in my application

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @authentication_errors @regression
  Scenario: Account retrieval without authentication
    Given I have no authentication token
    When I send a GET request to "/accounts/ACC001"
    Then I should receive an unauthorized error
    And the error message should indicate missing authorization
    And the WWW-Authenticate header should be present
    Then I restore the original authentication

  @authentication_errors @regression
  Scenario: Account creation with invalid token
    Given I have an invalid bearer token
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then I should receive an unauthorized error
    And the error message should indicate invalid token
    Then I restore the original authentication

  @authentication_errors @regression
  Scenario: Account operations with malformed authorization header
    When I send a request with malformed Authorization header
    And I send a GET request to "/accounts/ACC001"
    Then I should receive an unauthorized error
    Then I restore the original authentication

  @validation_errors @regression
  Scenario Outline: Account creation with invalid JSON
    When I send a POST request to "/accounts" with data:
      """
      <invalid_json>
      """
    Then the response status code should be 400
    And the response should contain an error message

    Examples:
      | invalid_json           |
      | {invalid json}         |
      | {"missing": "quote}    |
      | {"trailing": "comma",} |
      | {]                     |

  @validation_errors @regression
  Scenario: Account creation with empty request body
    When I send a POST request to "/accounts" with data:
      """
      {}
      """
    Then the response status code should be 400
    And the response should contain an error message

  @validation_errors @regression
  Scenario: Account creation with null values
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": null,
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @not_found_errors @regression
  Scenario Outline: Account retrieval for non-existent accounts
    When I send a GET request to "/accounts/<account_id>"
    Then the response status code should be 404
    And the response should contain an error message
    And the response should be valid JSON

    Examples:
      | account_id     |
      | NONEXISTENT   |
      | ACC999        |
      | DELETED001    |
      | ""            |

  @method_not_allowed @regression
  Scenario: Unsupported HTTP methods on account endpoints
    When I send a PUT request to "/accounts/ACC001"
    Then the response status code should be 405
    When I send a DELETE request to "/accounts/ACC001"
    Then the response status code should be 405
    When I send a PATCH request to "/accounts/ACC001"
    Then the response status code should be 405

  @request_size_limits
  Scenario: Account creation with oversized request
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "description": "This is an extremely long description that should exceed reasonable limits and test the API's ability to handle large request bodies. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo."
      }
      """
    Then the response status code should be 400

  @rate_limiting
  Scenario: Rapid consecutive account creation requests
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    And I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST002",
        "accountType": "SAVINGS", 
        "currency": "AUD"
      }
      """
    And I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST003",
        "accountType": "SAVINGS",
        "currency": "AUD"
      }
      """
    Then the response status code should be 201

  @concurrent_errors
  Scenario: Concurrent requests with authentication errors
    Given I have an invalid bearer token
    When I send concurrent requests with the same token
    Then all concurrent requests should be unauthorized
    Then I restore the original authentication

  @sql_injection_protection
  Scenario: Account operations with SQL injection attempts
    When I send a GET request to "/accounts/'; DROP TABLE accounts; --"
    Then the response status code should be 404
    And the response should contain an error message

  @xss_protection
  Scenario: Account creation with XSS payloads
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "description": "<script>alert('xss')</script>"
      }
      """
    Then the response status code should be 400
    And the response should contain an error message

  @unicode_handling
  Scenario: Account operations with Unicode characters
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "description": "Account description with international chars and symbols"
      }
      """
    Then the response status code should be 201

  @timeout_handling
  Scenario: Account operation timeout simulation
    # This would need to be implemented with network delays or slow responses
    When I send a GET request to "/accounts/ACC001"
    Then the response time should be under 5000 milliseconds

  @malformed_urls
  Scenario Outline: Account operations with malformed URLs
    When I send a GET request to "<malformed_url>"
    Then the response status code should be 404

    Examples:
      | malformed_url              |
      | /accounts//ACC001         |
      | /accounts/ACC001/         |
      | /accounts/ACC001/extra    |
      | /accounts/%20             |

  @content_length_mismatch
  Scenario: Account creation with mismatched content length
    Given I set the "Content-Length" header to "50"
    When I send a POST request to "/accounts" with data:
      """
      {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
      }
      """
    Then the response status code should be either 400 or 201

  @error_response_format
  Scenario: Verify error response format consistency
    When I send a GET request to "/accounts/NONEXISTENT"
    Then the response status code should be 404
    And the response should be valid JSON
    And the response should contain "error"
    And the response should contain "message"
    And the response should contain "timestamp"
    And the response should contain the correlation ID

  @security_headers_on_errors
  Scenario: Verify security headers are present in error responses
    When I send a GET request to "/accounts/NONEXISTENT"
    Then the response status code should be 404
    And the response should include security headers
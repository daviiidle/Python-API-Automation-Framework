@api @banking @authentication @security @regression
Feature: Authentication and Security
  As a banking API
  I want to ensure secure access to banking services
  So that only authorized clients can access sensitive data

  Background:
    Given the banking API is available

  @authentication @smoke @quarantine
  Scenario: Successful API access with valid bearer token
    Given I have a valid bearer token
    When I send a GET request to "/customers/CUST001"
    Then the response should be successful
    And the response should contain the correlation ID

  @authentication @error_handling
  Scenario: API access denied without authentication token
    Given I have no authentication token
    When I send a GET request to "/customers/CUST001"
    Then I should receive an unauthorized error
    And the error message should indicate missing authorization
    And the WWW-Authenticate header should be present
    Then I restore the original authentication

  @authentication @error_handling
  Scenario: API access denied with invalid token
    Given I have an invalid bearer token
    When I send a GET request to "/customers/CUST001"
    Then I should receive an unauthorized error
    And the error message should indicate invalid token
    Then I restore the original authentication

  @security @regression @quarantine
  Scenario: Authentication is case-sensitive
    Given I have a valid bearer token
    When I send a GET request to "/customers/CUST001"
    Then the response should be successful
    Then the authentication should be case-sensitive

  @concurrency @security
  Scenario: Concurrent requests with same valid token
    Given I have a valid bearer token
    When I send concurrent requests with the same token
    Then all concurrent requests should succeed

  @security @headers
  Scenario: Security headers are present in responses
    Given I have a valid bearer token
    When I send a GET request to "/customers/CUST001"
    Then the response should include security headers
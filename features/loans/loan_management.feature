@api @banking @loans @regression @dynamic_data
Feature: Loan Management
  As a banking API client
  I want to manage loan applications
  So that customers can apply for various types of loans

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create loan application with generated data
    Given I generate test data for "loan"
    When I create a "loan" using generated data
    Then the response status code should be 201
    And the response should contain "loanId"
    And the response should contain "customerId"
    And the response should contain "loanType"
    And the response should contain "amount"
    And the response should contain "term"

  @table_driven @regression
  Scenario: Create loans with various types and terms
    When I create loans with the following data:
      | loanType  | amount   | term | interestRate |
      | PERSONAL  | 25000    | 36   | 8.5         |
      | HOME      | 450000   | 300  | 4.2         |
      | CAR       | 35000    | 60   | 6.8         |
      | BUSINESS  | 100000   | 84   | 9.5         |
    Then all loan creations should have the expected results
@api @banking @term_deposits @regression @dynamic_data
Feature: Term Deposit Management
  As a banking API client
  I want to manage term deposits
  So that customers can invest in fixed-term deposits

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create term deposit with generated data
    Given I generate test data for "term_deposit"
    When I create a "term_deposit" using generated data
    Then the response status code should be 201
    And the response should contain "depositId"
    And the response should contain "customerId"
    And the response should contain "principal"
    And the response should contain "termMonths"
    And the response should contain "interestRate"

  @table_driven @regression
  Scenario: Create term deposits with various terms and amounts
    When I create term deposits with the following data:
      | principal | termMonths | interestRate | compoundingFrequency |
      | 5000      | 6          | 3.5         | MONTHLY             |
      | 25000     | 12         | 4.2         | QUARTERLY           |
      | 50000     | 24         | 5.0         | ANNUALLY            |
      | 100000    | 36         | 5.5         | QUARTERLY           |
    Then all term deposit creations should have the expected results
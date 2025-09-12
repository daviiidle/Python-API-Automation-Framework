@api @banking @bookings @regression @dynamic_data
Feature: Booking Management
  As a banking API client
  I want to manage appointment bookings
  So that customers can schedule banking services

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @happy_path @smoke
  Scenario: Successfully create booking with generated data
    Given I generate test data for "booking"
    When I create a "booking" using generated data
    Then the response status code should be 201
    And the response should be valid JSON
    And the response should contain "bookingId"
    And the response should contain "customerId"
    And the response should contain "serviceType"
    And the response should contain "bookingDate"
    And the response should contain "bookingTime"

  @table_driven @regression
  Scenario: Create bookings with various service types
    When I create accounts with the following data:
      | serviceType        | bookingDate | bookingTime | branch          |
      | APPOINTMENT       | 2024-02-15  | 10:00      | Melbourne CBD   |
      | CONSULTATION      | 2024-02-16  | 14:30      | Sydney North    |
      | LOAN_MEETING      | 2024-02-17  | 09:00      | Brisbane South  |
      | INVESTMENT_ADVICE | 2024-02-18  | 15:00      | Perth Central   |
    Then all account creations should have the expected results

  @conflict_handling @error_handling
  Scenario: Attempt to create conflicting bookings
    Given I generate test data for "booking"
    When I create a "booking" using generated data
    Then the response status code should be 201
    When I create a "booking" using generated data
    Then the response status code should be 409
    And the response should contain an error message
@networks
Feature: Actions for Keys

  Background:
    Given I am logged in to mist.core
    And I am in the new UI
    When I wait for the dashboard to load

  @network-add
  Scenario: Add Network
    Given "Openstack" cloud has been added
    When I visit the Networks page
    When I click the button "+"
    Then I expect the "network" add form to be visible within max 10 seconds
    When I set the value "network_random" to field "Name" in "network" add form
    Then I open the "Cloud" drop down
    And I wait for 1 seconds
    When I click the button "Openstack" in the "Cloud" dropdown
    And I expect for the button "Add" in "network" add form to be clickable within 3 seconds
    When I focus on the button "Add" in "network" add form
    And I click the button "Add" in "network" add form
    Then I expect the "network" edit form to be visible within max 5 seconds
    Then I expect the "network" edit form to be visible within max 5 seconds
    When I visit the Networks page
    Then "network_random" network should be present within 30 seconds
    Then I visit the Home page
    When I wait for the dashboard to load

  @network-delete
  Scenario: Delete Key
    When I visit the Networks page
    When I click the "network_random" "network"
    Then I expect for the button "Delete" in "network" edit form to be clickable within 5 seconds
    And I expect the "network" edit form to be visible within max 5 seconds
    Then I click the button "Delete" in "network" edit form
    And I expect the dialog "Delete Network" is open within 4 seconds
    And I click the "Delete" button in the dialog "Delete Network"
    And I expect the dialog "Delete Network" is closed within 4 seconds
    Then "network_random" network should be absent within 30 seconds
    Then I wait for 3 seconds
    Then I visit the Home page
    And I wait for the dashboard to load
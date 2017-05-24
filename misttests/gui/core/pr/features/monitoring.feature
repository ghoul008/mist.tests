@monitoring
Feature: Create Machine and test monitoring


  @enable-monitoring
  Scenario: Create Machine,deploy monitoring agent and check the graphs
    Given I am logged in to mist.core
    And cloud Docker-Monitoring has been added via API request
    And "Key1" key has been added



    When I visit the Machines page
    And I wait for 1 seconds
    And I click the button "+"
    Then I expect the "Machine" add form to be visible within max 5 seconds
    When I open the "Choose Cloud" drop down
    And I wait for 1 seconds
    When I click the button "Docker" in the "Choose Cloud" dropdown
    Then I expect the field "Machine name" in the machine add form to be visible within max 4 seconds
    # give machine below a random name, such as with create_machine test
    When I select the proper values for "Docker" to create the "docker-ui-test" machine
    And I click the "enable monitoring" button
    Then I click the "Launch" button
    And I wait for 3 seconds
    Then I visit the Machines page
    Then "docker-ui-test" machine state has to be "running" within 30 seconds
    When I click the "docker-ui-test" "machine"
    # check if all 9 panels have appeared.... // is it always 9 panels?
    Then 9 graphs should be visible within max 20 seconds

  @add-custom-graph
  Scenario: Add custom graph and make sure an extra graph is visible
    When I click the "Add graph" button
    Then I expect the dialog "Select target for graph" is open within 5 seconds
    When I select "entropy" in the dialog "Select target for graph"
    And I wait for 2 seconds
    Then 10 graphs should be visible within max 20 seconds

  @disable-monitoring
  Scenario: Disable monitoring
    When I visit the Machines page
    And I click the "docker-ui-test" "machine"
    When I click the "Disable Monitoring" button
    Then I expect the dialog "Disable Machine Monitoring" is open within 5 seconds 
    When I click the "Disable Monitoring" button in the dialog "Disable Machine Monitoring"
    Then I expect the dialog "Disable Machine Monitoring" is closed within 5 seconds
    Then 0 graphs should be visible within max 20 seconds

#    And I expect for "dialog-popup" modal to appear within max 400 seconds
#    And I click the "_x_" button inside the "Success" modal
#    When I focus on the "third" button
#    And I click the button "third"
#    Then I expect for "single-machine-page" page to appear within max 4 seconds
#    And I wait for the graphs to appear


# create a machine with enable_monitoring=True
# w8 to see some graphs...
# probably check 2 graphs?
# add an extra graph
# disable monitoring
# verify that there are no graphs visible
# click on enable-monitoring
# w8 to see some graphs...

# kill machine at the end of the test
# unit steps that add cloud via API
# add key via API request

# probably associate a key in between?

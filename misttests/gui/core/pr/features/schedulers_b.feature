@schedulers_v2
Feature: Schedulers

  @scheduler-add-crontab
  Scenario: Add schedule
    Given I am logged in to mist.core
    And "Docker" cloud has been added
    When I visit the Machines page
    Then "ui-testing-machine-2" machine state has to be "running" within 10 seconds
    When I visit the Schedules page
    And I click the button "+"
    Then I expect the "schedule" add form to be visible within max 10 seconds
    When I set the value "TestScheduler" to field "Name" in "schedule" add form
    And I open the "Task" drop down
    And I wait for 1 seconds
    And I click the button "stop" in the "Task" dropdown
    And I wait for 1 seconds
    And I select "Specific Machines" from "ids_or_tags" radio-group
    And I wait for 1 seconds
    And I select the "ui-testing-machine-2" checkbox
    And I select "Crontab" from "schedule_type" radio-group
    #When I set the value "2" to field "Maximum Run Count" in "schedule" add form
    And I set the value "*****" to field "Crontab" in "schedule" add form
    And I click the button "Add" in "schedule" add form
    And I wait for 1 seconds
    When I visit the Home page
    And I visit the Schedules page
    Then "TestScheduler" schedule should be present within 3 seconds

  @add-script
    # to be replaced with API call
  Scenario: Add a script that will be used for the scheduler
    When I visit the Scripts page
    When I click the button "+"
    Then I expect the "Script" add form to be visible within max 10 seconds
    When I set the value "<name>" to field "Script Name" in "script" add form
    And I open the "Type" drop down
    And I wait for 2 seconds
    When I click the button "<type>" in the "Type" dropdown
    And I wait for 2 seconds
    And I open the "Source" drop down
    And I wait for 2 seconds
    And I click the button "<source>" in the "Source" dropdown
    When I set the value "<script>" to field "<field>" in "script" add form
    When I focus on the button "Add" in "script" add form
    And I expect for the button "Add" in "script" add form to be clickable within 3 seconds
    And I click the button "Add" in "script" add form
    And I wait for 3 seconds
    When I visit the Scripts page after the counter has loaded
    # FIXME: below has been commented out because script is not available immediately..need for redirection to another page first...
    # FIXME: instead of redirecting to home, an option is to sort the items...
    Then I visit the Home page
    When I wait for the dashboard to load
    When I visit the Scripts page
    Then "<name>" script should be present within 3 seconds

  @check-machines-state
  Scenario: Check machine's state
    When I visit the Machines page
    Then "ui-testing-machine" machine state has to be "stopped" within 75 seconds

# run script

# just check starts and expires
# enable-disable

# machines-with tags
# update -machine (from api-test-1 to api-test-2)

from behave import step, use_step_matcher
from behave import given

from time import time
from time import sleep

from random import randrange

from .utils import safe_get_element_text, get_page_element, expand_shadow_root
from .utils import get_page, clear_input_and_send_keys

from .buttons import clicketi_click, click_button_from_collection

from selenium.webdriver.common.keys import Keys

from selenium.webdriver import ActionChains

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException


comparisons = {"==": lambda x, y: x == y,
               ">": lambda x, y: x > y,
               "<": lambda x, y: x < y,
               ">=": lambda x, y: x >= y,
               "<=": lambda x, y: x <= y,
               "!=": lambda x, y: x != y,
               }

machine_states_ordering = {
    'error': 6,
    'pending': 5,
    'rebooting': 4,
    'running': 3,
    'unknown': 2,
    'suspended': 2,
    'terminated': 1,
    'undefined': 1,
    'stopped': 0
}

# this dict contains image, size and location to be tested for each provider
machine_values_dict = {
    "aws": ["Ubuntu Server 16.04 Beta2 (PV)", "m1.small - Small Instance", "ap-northeast-1a "],
    "digital ocean": ["Ubuntu 14.04.5 x64", "512mb", "Amsterdam 2"],
    "packet": ["Ubuntu 14.04 LTS", "Type 0 - 8GB RAM", "Amsterdam, NL"],
    "openstack": ["CoreOS", "m1.tiny", "0"],
    "rackspace": ["Ubuntu 14.04 LTS (Trusty Tahr) (PV)", "512MB Standard Instance", "0"],
    "softlayer": ["Ubuntu - Latest (64 bit) ", "1 CPU, 1GB ram, 25GB ", "AMS01 - Amsterdam"],
    "azure": ["Ubuntu Server 14.04 LTS", "ExtraSmall (1 cores, 768 MB) ", "West Europe"],
    "docker": ["Ubuntu 14.04 - mist.io image"]
}

@step(u'I click the other server machine')
def click_bare_metal_machine(context):
    context.execute_steps(u'Then I click on list item "%s" machine' % context.mist_config['bare_metal_host'])


def set_values_to_create_machine_form(context,provider,machine_name):
    context.execute_steps(u'''
                Then I set the value "%s" to field "Machine Name" in the "machine" add form
                When I open the "Image" dropdown in the "machine" add form
                And I click the "%s" button in the "Image" dropdown in the "machine" add form
                And I open the "Key" dropdown in the "machine" add form
                And I click the "DummyKey" button in the "Key" dropdown in the "machine" add form
                And I wait for 1 seconds
            ''' % (machine_name,
                   machine_values_dict.get(provider)[0]))

    if 'digital ocean' in provider:
        context.execute_steps(u'''
                    When I open the "Size" drop down in the "machine" add form
                    And I click the "%s" button in the "Size" dropdown in the "machine" add form
                    When I open the "Location" drop down in the "machine" add form
                    And I click the "%s" button in the "Location" dropdown in the "machine" add form
                ''' % ( machine_values_dict.get(provider)[1],
                       machine_values_dict.get(provider)[2]))


@step(u'I select the proper values for "{provider}" to create the "{machine_name}" machine')
def cloud_creds(context, provider, machine_name):
    provider = provider.strip().lower()
    if provider not in machine_values_dict.keys():
        raise Exception("Unknown cloud provider")
    set_values_to_create_machine_form(context, provider, machine_name)


@step(u'I expect for "{key}" key to appear within max {seconds} seconds')
def key_appears(context, key, seconds):
    if context.mist_config.get(key):
        key_name = context.mist_config.get(key)
    timeout = time() + int(seconds)
    while time() < timeout:
        try:
            for key_in_list in context.browser.find_elements_by_class_name('small-list-item'):
                if key_name == safe_get_element_text(key_in_list):
                    actions = ActionChains(context.browser)
                    actions.send_keys(Keys.ESCAPE)
                    actions.perform()
                    return True
                else:
                    pass
        except:
            sleep(1)
    assert False, "Key %s did not appear after %s seconds" % (key,seconds)


@step(u'I choose the "{name}" machine')
def choose_machine(context, name):
    if context.mist_config.get(name):
        name = context.mist_config.get(name)
    end_time = time() + 20
    while time() < end_time:
        machine = get_machine(context, name)
        if machine:
            checkbox = machine.find_element_by_tag_name("mist-check")
            checkbox.click()
            return

        sleep(2)
    assert False, u'Could not choose/tick %s machine' % name


@step(u'I should see the "{name}" machine added within {seconds} seconds')
def assert_machine_added(context, name, seconds):
    if context.mist_config.get(name):
        name = context.mist_config.get(name)

    end_time = time() + int(seconds)
    while time() < end_time:
        machine = get_machine(context, name)
        if machine:
            return
        sleep(2)

    assert False, u'%s is not added' % name


def get_machine(context, name):
    try:
        placeholder = context.browser.find_element_by_tag_name("page-machines").find_element_by_id("items")
        machines = placeholder.find_elements_by_tag_name("vaadin-grid-table-row")

        for machine in machines:
            machine_text = safe_get_element_text(machine)
            if name in machine_text:
                return machine

        return None
    except NoSuchElementException:
        return None
    except StaleElementReferenceException:
        return None

@step(u'I wait for probing to finish for {seconds} seconds max')
def wait_for_loader_to_finish(context, seconds):
    rows = context.browser.find_elements_by_tag_name('tr')
    for row in rows:
        cells = row.find_elements_by_tag_name('td')
        cells_text = safe_get_element_text(cells[0])
        if cells_text == 'Last probed':
            end_time = time() + int(seconds)
            while time() < end_time:
                try:
                    cells[1].find_element_by_class_name('ajax-loader')
                    sleep(1)
                except NoSuchElementException:
                    sleep(1)
                    return
            assert False, "Ajax loading hasn't finished after %s seconds" % seconds
    assert False, "Could not locate ajax loader"


@step(u'probing was successful')
def check_probing(context):
    rows = context.browser.find_elements_by_tag_name('tr')
    for row in rows:
        cells = row.find_elements_by_tag_name('td')
        cells_zero_text = safe_get_element_text(cells[0])
        if cells_zero_text == 'Last probed':
            cells_one_text = safe_get_element_text(cells[1])
            message = cells_one_text.split('\n')[0].lower()
            assert message == 'just now', "Probing of machine failed" \
                                          "(message is: %s)" % cells_one_text
            return
    assert False, "Could not find any line about probing"


@step(u'I give a default script for python script')
def fill_default_script(context):
    textfield = context.browser.find_element_by_id("custom-plugin-script")
    textfield.clear()
    my_script ="import time\n\ntry:\n    from urllib2 import urlopen \n\n" \
               "except ImportError:\n    from urllib import urlopen\n" \
               "URL = 'https://mist.io'\n\n" \
               "TEXT = 'GOVERN YOUR CLOUDS'\nCHECK_TIMES = 10\nRESULT = -1\n\n" \
               "def read():\n    global CHECK_TIMES\n    global RESULT\n" \
               "    if CHECK_TIMES < 10:\n        CHECK_TIMES += 1\n        return RESULT\n" \
               "    CHECK_TIMES = 0\n\n    start=time.time()\n    try:\n" \
               "        nf=urlopen(URL)\n    except:\n        RESULT = -1\n" \
               "        return RESULT\n    page=nf.read()\n    end=time.time()\n" \
               "    nf.close()\n    if TEXT in page:\n        RESULT = end - start\n" \
               "    else:\n        RESULT =  -1\n    return RESULT"
    for letter in my_script:
        textfield.send_keys(letter)


@step(u'rule "{rule}" should be {state} in the "{page}" page')
def verify_rule_is_present(context, rule, state, page):
    found = False
    state = state.lower()
    if state not in ['present', 'absent']:
        raise Exception('Unknown state %s' % state)
    page_element = get_page(context, page)
    page_shadow = expand_shadow_root(context, page_element)
    rules = page_shadow.find_element_by_css_selector('mist-rules').text.replace('\n','').replace(' ','').lower()
    rule = rule.replace(" ", "").lower()
    if rule in rules:
        found = True
    if state == 'present' and found:
        return True
    if state == 'absent' and not found:
        return True
    assert False, "Rule %s was not %s in existing rules for the monitored machine" % (rule, state)


@step(u'"{key}" key should be associated with the machine "{machine}"')
def check_for_associated_key(context, key, machine):
    page = get_page(context, "machine")
    page_shadow = expand_shadow_root(context, page)
    machine_keys_class = page_shadow.find_elements_by_css_selector('div.associatedKeys > div.machine-key')
    for element in machine_keys_class:
        if safe_get_element_text(element) == key:
            return
    assert False, "The key has not been associated with the machine!"


use_step_matcher("re")
@step(u'"(?P<key>[A-Za-z0-9]+)" key should be associated with the machine "(?P<machine>[A-Za-z0-9 \-]+)" within (?P<seconds>[0-9]+) seconds')
def check_for_associated_key_within(context, key, machine, seconds):
    timeout = time() + int(seconds)
    page = get_page(context, "machine")
    page_shadow = expand_shadow_root(context, page)
    while time() < timeout:
        machine_keys_class = page_shadow.find_elements_by_css_selector('div.associatedKeys > div.machine-key')
        for element in machine_keys_class:
            if safe_get_element_text(element) == key:
                return
        sleep(1)
    assert False, "The key has not been associated with the machine!"


use_step_matcher("parse")
@step(u'I delete the associated key "{key}"')
def disassociate_key(context, key):
    _, page = get_page_element(context, "machines", "machine")
    page_shadow = expand_shadow_root(context, page)
    machine_keys_class = page_shadow.find_elements_by_css_selector('div.associatedKeys > div.machine-key')
    for element in machine_keys_class:
        if safe_get_element_text(element) == key:
            delete_btn = element.find_element_by_css_selector('.delete')
            clicketi_click(context, delete_btn)
            return


@step(u'there should be {keys} keys associated with the machine within {seconds} seconds')
def keys_associated_with_machine(context, keys, seconds):
    timeout = time() + int(seconds)
    _, page = get_page_element(context, "machines", "machine")
    page_shadow = expand_shadow_root(context, page)
    while time() < timeout:
        machine_keys_class = page_shadow.find_elements_by_css_selector('div.associatedKeys > div.machine-key')
        associated_keys_with_machine = 0
        for element in machine_keys_class:
            try:
                element.find_element_by_tag_name('a')
                associated_keys_with_machine += 1
            except:
                pass
        if associated_keys_with_machine == int(keys):
            return
        sleep(1)
    assert False, "There are %s keys associated with the machine" % associated_keys_with_machine


@step(u'I set an expiration in "{exp_num}" "{exp_unit}" with a notify of "{notify_num}" "{notify_unit}" before')
def set_expiration(context, exp_num, exp_unit, notify_num, notify_unit):
    from .forms import get_add_form
    form = get_add_form(context, 'machine')
    form_shadow = expand_shadow_root(context, form)
    sub_form = form_shadow.find_element_by_css_selector('app-form')
    sub_form_shadow = expand_shadow_root(context, sub_form)
    # TODO: cleanup
    sub_fieldgroup = sub_form_shadow.find_element_by_css_selector('sub-fieldgroup')
    # find proper one...
    assert sub_fieldgroup.text.startswith('Set expiration'), False
    sub_field_shadow = expand_shadow_root(context, sub_fieldgroup)
    nested_app_form=sub_field_shadow.find_element_by_tag_name('app-form')
    nested_app_form_shadow = expand_shadow_root(context, nested_app_form)
    dur_fields=nested_app_form_shadow.find_elements_by_tag_name('duration-field')
    expiration=dur_fields[0]
    notify=dur_fields[1]
    expiration_shadow_root=expand_shadow_root(context, expiration)
    exp_input=expiration_shadow_root.find_element_by_tag_name('paper-input')
    clear_input_and_send_keys(exp_input, exp_num)
    exp_dropdown=expiration_shadow_root.find_element_by_tag_name('paper-dropdown-menu')
    exp_dropdown.click()
    sleep(0.5)
    buttons = exp_dropdown.find_elements_by_css_selector('paper-item')
    click_button_from_collection(context, exp_unit, buttons)

    notify_shadow_root=expand_shadow_root(context, notify)
    notify_input=notify_shadow_root.find_element_by_tag_name('paper-input')
    clear_input_and_send_keys(notify_input, notify_num)
    notify_dropdown=notify_shadow_root.find_element_by_tag_name('paper-dropdown-menu')
    notify_dropdown.click()
    sleep(0.5)
    buttons = notify_dropdown.find_elements_by_css_selector('paper-item')
    click_button_from_collection(context, notify_unit, buttons)

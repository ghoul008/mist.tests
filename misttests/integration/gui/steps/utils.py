from behave import step

from time import time
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains


def safe_get_element_text(check_element):
    try:
        return check_element.text
    except StaleElementReferenceException:
        return ""


def give_some_input(context, input_element, text):
    if context.mist_config.get(text):
        text = context.mist_config[text]
    actions = ActionChains(context.browser)
    actions.move_to_element(input_element)
    actions.click(input_element)
    actions.send_keys(text)
    actions.perform()


def get_page_element(context, page=None, subpage=None):
    mist_app = context.browser.find_element_by_tag_name('mist-app')
    if not page:
        page = mist_app.get_attribute('page')
    mist_app_shadow = expand_shadow_root(context, mist_app)
    page_css_selector = 'iron-pages > page-%s' % page
    page_element = mist_app_shadow.find_element_by_css_selector(page_css_selector)
    if subpage:
        page_shadow = expand_shadow_root(context, page_element)
        return page_element, page_shadow.find_element_by_css_selector(subpage + '-page')
    return page_element


@step(u'I type "{some_text}" in input with id "{element_id}" within "{container_id}"')
def give_some_input_by_id_within_container(context, some_text, element_id, container_id=None):
    if not container_id:
        input_element = context.browser.find_element_by_id(element_id)
    else:
        container = context.browser.find_element_by_id(container_id)
        input_element = container.find_element_by_id(element_id)
    give_some_input(context, input_element, some_text)


@step(u'I type "{some_text}" in input with id "{element_id}"')
def give_some_input_by_id(context, some_text, element_id):
    give_some_input_by_id_within_container(context, some_text, element_id)


@step(u'I type "{some_text}" in input with class name "{element_class}" within "{container_id}"')
def give_some_input_by_class_within_container(context, some_text, element_class, container_id=None):
    if not container_id:
        input_element = context.browser.find_element_by_class_name(element_class)
    else:
        input_element = context.browser.find_element_by_id(container_id).find_element_by_class_name(element_class)
    give_some_input(context, input_element, some_text)


@step(u'I type "{some_text}" in input with class name "{element_class}"')
def give_some_input_by_class(context, some_text, element_class):
    give_some_input_by_class_within_container(context, some_text, element_class)


def focus_on_element(context, element):
    position = element.location
    from navigation import found_one
    assert found_one(context), "I have no idea where I am"
    try:
        context.browser.find_element_by_tag_name("mist-app")
        js = "document.querySelector('paper-header-panel').scroller.scrollTop = %s" % position['y']
        context.browser.execute_script(js)
    except:
        context.browser.execute_script("window.scrollTo(0, %s)" % position['y'])


@step(u'I wait for {seconds} seconds')
def wait(context, seconds):
    sleep(int(seconds))


@step(u'the title should be "{text}"')
def assert_title_is(context, text):
    assert text == context.browser.title


@step(u'the title should contain "{text}"')
def assert_title_contains(context, text):
    assert text in context.browser.title


@step(u'{counter_title} counter should be greater than {counter_number} within '
      u'{seconds} seconds')
def some_counter_loaded(context, counter_title, counter_number, seconds):
    counter_title = counter_title.lower()
    if counter_title not in ['machines', 'images', 'keys', 'networks',
                             'tunnels', 'scripts', 'templates', 'stacks',
                             'teams', 'zones']:
        raise ValueError('The counter given is unknown')
    try:
        counter = context.browser.find_element_by_css_selector('a#%s.mist-sidebar'
                                                               % counter_title)
    except NoSuchElementException:
        raise NoSuchElementException("Counter with name %s has not been found"
                                     % counter_title)

    end_time = time() + int(seconds)
    while time() < end_time:
        counter_span = counter.find_element_by_css_selector("span.count")
        counter_span_text = safe_get_element_text(counter_span)
        counter_span_text = "0" if not counter_span_text else counter_span_text
        if int(counter_span_text) > int(counter_number):
            return
        else:
            sleep(2)

    assert False, 'The counter did not say that more than %s images were ' \
                  'loaded' % counter_number


@step(u'I should see a header with title "{text}"')
def see_header_with_title(context, text):
    titles = context.browser.find_elements_by_class_name("ui-title")
    for title in titles:
        title_text = safe_get_element_text(title)
        if text in title_text:
            return

    assert False, u'Could not find title with text %s in the page' % text


def wait_for_element_to_be_visible(context, search_tuple, seconds, error_message):
    try:
        WebDriverWait(context.browser, int(seconds)).until(
            EC.visibility_of_element_located(search_tuple))
    except TimeoutException:
        raise TimeoutException(error_message)


def wait_for_element_in_container_to_be_visible(container, search_tuple,
                                                seconds, error_message):
    try:
        WebDriverWait(container, int(seconds)).until(
            EC.visibility_of_element_located(search_tuple))
    except TimeoutException:
        raise TimeoutException(error_message)


@step(u'I expect for "{element_id}" to be visible within max {seconds} '
      u'seconds')
def become_visible_waiting_with_timeout(context, element_id, seconds):
    msg = "element with id %s did not become visible after %s seconds"\
          % (element_id, seconds)
    wait_for_element_to_be_visible(context, (By.ID, element_id),
                                   int(seconds), msg)


@step(u'I expect for "{page_title}" page to appear within max {seconds} seconds')
def check_page_is_visible(context, page_title, seconds):
    page = page_title.lower()
    if page not in ['machines', 'images', 'keys', 'networks', 'tunnels',
                    'scripts', 'schedules', 'templates', 'stacks', 'insights', 'teams',
                    'zones', 'rules']:
        raise ValueError('The page given is unknown')
    mist_app = context.browser.find_element_by_tag_name('mist-app')
    mist_app_shadow = expand_shadow_root(context, mist_app)
    page_css_selector = 'iron-pages > page-%s' % page
    page_element = mist_app_shadow.find_element_by_css_selector(page_css_selector)
    if page in ['machines', 'images', 'teams','keys', 'networks',
                'scripts', 'schedules', 'templates', 'stacks', 'zones']:
        container = expand_shadow_root(context, page_element)
        # Retry a few times because the shadow root won't always get expanded right away
        timeout = 5
        while timeout and not container:
            sleep(1)
            timeout -= 1
            container = expand_shadow_root(context, page_element)
        selector = (By.CSS_SELECTOR, 'mist-list')
    elif page in ['insights', 'rules']:
        container = mist_app_shadow
        selector = (By.CSS_SELECTOR, page_css_selector)
    msg = "%s page is not visible after %s seconds" % (page, seconds)
    wait_for_element_in_container_to_be_visible(container, selector,
        int(seconds), msg)


@step(u'I should read "{something}" in input with id "{input_id}"')
def check_input_for_text(context, something, input_id):
    input = None
    try:
        input = context.browser.find_element_by_id(input_id)
    except NoSuchElementException:
        pass
    assert input, 'Could not find element with id %s' % input_id
    assert input.get_attribute('value').lower() == something.lower(), \
        "Input text did not match what was expected"


def wait_until_visible(element, seconds):
    timeout = time() + seconds
    while time() < timeout:
        if element.is_displayed():
            return True
        sleep(1)
    raise TimeoutException("Element has not become visible after %s seconds"
                           % seconds)


def expand_shadow_root(context, element):
    return context.browser.execute_script('return arguments[0].shadowRoot', element)


def expand_slot(context, element):
    return context.browser.execute_script('return arguments[0].assignedElements()', element)


def get_grid_items(context, grid):
    return context.browser.execute_script('return arguments[0].items', grid)

def get_list_item_from_checkbox(context, checkbox):
    return context.browser.execute_script('return arguments[0].item', checkbox)

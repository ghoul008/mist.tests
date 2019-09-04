from time import time
from time import sleep

from behave import step, use_step_matcher

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

from .utils import safe_get_element_text, expand_shadow_root, get_page

from .buttons import click_button_from_collection, clicketi_click

from .forms import get_input_element_from_form
from .forms import clear_input_and_send_keys, get_button_from_form


def get_dialog(context, title):
    import ipdb; ipdb.set_trace()
    title = title.lower()
    try:
        overlay = context.browser.find_element_by_tag_name('vaadin-dialog-overlay')
        overlay_shadow = expand_shadow_root(context, overlay)
        dialog = overlay_shadow.find_element_by_css_selector('div#content')
        dialog_shadow = expand_shadow_root(context, dialog)

        if dialog.is_displayed():
            try:
                dialog = dialog_shadow.find_element_by_css_selector('team-add-element, custom-graph')
                dialog_shadow = expand_shadow_root(context, dialog)
            except NoSuchElementException:
                pass
            try:
                t = safe_get_element_text(dialog_shadow.find_element_by_css_selector(
                    'h2')).strip().lower()
            except NoSuchElementException:
                # single cloud page
                t = safe_get_element_text(dialog_shadow.find_element_by_css_selector(
                    'h3')).strip().lower()
            if title in t:
                return dialog
    except NoSuchElementException:
        pass
    return None


@step(u'I expect the "{dialog_title}" dialog to be {state} within {seconds}'
      u' seconds')
def wait_for_dialog(context, dialog_title, state, seconds):
    state = state.lower()
    if state not in ['open', 'closed']:
        raise Exception('Unknown state %s' % state)
    timeout = time() + int(seconds)
    while time() < timeout:
        dialog = get_dialog(context, dialog_title)
        if state == 'open' and dialog:
            return True
        if state == 'closed' and not dialog:
            return True
        sleep(1)
    assert False, "Dialog with title %s has not %s after %s seconds" \
                  % (dialog_title, state, seconds)


@step(u'I expect the field "{field_name}" in the dialog with title '
      u'"{dialog_title}" to be visible within max {seconds} seconds')
def check_that_field_is_visible(context, field_name, dialog_title, seconds):
    field_name = field_name.lower()
    dialog = get_dialog(context, dialog_title)
    dialog_shadow = expand_shadow_root(context, dialog)
    input_element = None
    timeout = time() + int(seconds)
    while time() < timeout:
        input_element = get_input_element_from_form(context, dialog_shadow, field_name)
        if input_element.is_displayed():
            return True
        sleep(1)
    assert input_element, "Could not find field %s after %s seconds" % field_name
    assert False, "Field %s did not become visible after %s seconds" \
                  % (field_name, seconds)


#@step(u'I click the "{button_name}" button in the "{dialog_title}" dialog')
use_step_matcher("re")
@step(u'I click the "(?P<button_name>[A-Za-z0-9_\. ]+)" button in the "(?P<dialog_title>[A-Za-z ]+)" dialog')
def click_button_in_dialog(context, button_name, dialog_title):
    dialog = get_dialog(context, dialog_title)
    assert dialog, "Could not find dialog with title %s" % dialog_title
    dialog_shadow = expand_shadow_root(context, dialog)
    button = get_button_from_form(context, dialog_shadow, button_name, tag_name='paper-button:not([hidden]), paper-item:not([hidden])')
    clicketi_click(context, button)


use_step_matcher("parse")
@step(u'I click the toggle button with id "{btn_id}" in the "{dialog}" dialog')
def click_toggle_button_in_dialog(context, btn_id, dialog):
    open_dialog = get_dialog(context, dialog)
    assert open_dialog, "Could not find dialog with title %s" % dialog
    dialog_shadow = expand_shadow_root(context, open_dialog)
    button_to_click = dialog_shadow.find_element_by_css_selector('#%s' % btn_id)
    clicketi_click(context, button_to_click)


@step(u'I set the value "{value}" to field "{name}" in the "{title}" dialog')
def set_value_to_field(context, value, name, title):
    if context.mist_config.get(value):
        value = context.mist_config.get(value)
    dialog = get_dialog(context, title)
    dialog_shadow = expand_shadow_root(context, dialog)
    input_element = get_input_element_from_form(context, dialog_shadow, name.lower())
    assert input_element, "Could not set value to field %s" % name
    clear_input_and_send_keys(input_element, value)


@step(u'there should be a "{error_msg}" error message'
      u' in the "{dialog_title}" dialog')
def check_errormsg_in_dialog(context, error_msg, dialog_title):
    dialog = get_dialog(context, dialog_title)
    dialog_shadow = expand_shadow_root(context, dialog)
    error_element = dialog_shadow.find_element_by_css_selector('#errormsg')
    if error_msg in safe_get_element_text(error_element):
        return
    assert False, "%s is not part of the error message" % error_msg
    
    
"""Extra Steps and Methods for resolving test cases 
   in the machine UI integration tests.
"""
@step(u'I expect the "{dialog_title}" machine dialog to be {state} within {seconds}'
      u' seconds')
def wait_for_machine_dialog(context, dialog_title, state, seconds):
    state = state.lower()
    if state not in ['open', 'closed']:
        raise Exception('Unknown state %s' % state)
    timeout = time() + int(seconds)
    while time() < timeout:
        dialog = get_machine_actions_dialog(context, dialog_title)
        if state == 'open' and dialog:
            return True
        if state == 'closed' and not dialog:
            return True
        sleep(1)
    assert False, "Dialog with title %s has not %s after %s seconds" \
                  % (dialog_title, state, seconds)
              
def get_machine_actions_dialog(context, title):
    title = title.lower()
    try:
        page = get_page(context, "machine")
        page_shadow = expand_shadow_root(context, page)
        content = page_shadow.find_element_by_css_selector('div#content')
        paper_material = content.find_element_by_tag_name('paper-material')
        
        machine_actions = paper_material.find_element_by_tag_name('machine-actions')
        machine_actions_shadow = expand_shadow_root(context, machine_actions)
        machine_edit = machine_actions_shadow.find_element_by_tag_name('machine-edit')
        machine_edit_shadow = expand_shadow_root(context, machine_edit)
        paper_dialog = machine_edit_shadow.find_element_by_tag_name('paper-dialog')
        
        if paper_dialog.is_displayed():
            try:
                t = safe_get_element_text(paper_dialog.find_element_by_css_selector(
                    'h2')).strip().lower()
            except NoSuchElementException:
                pass
            if title in t:
                return paper_dialog
        return         
    except NoSuchElementException:
        pass
    return None

                                                          
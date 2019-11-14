from behave import step

from time import time
from time import sleep

from .utils import safe_get_element_text, get_page_element, expand_shadow_root, get_grid_items

import logging

# log = logging.getLogger(__name__)
#
# logging.basicConfig(level=logging.INFO)


def find_image(image, images_list):
    for check_image in images_list:
        if image in safe_get_element_text(check_image):
            return check_image.find_element_by_css_selector('strong.name')


@step(u'the "{image}" image should be "{state}" within {seconds} seconds')
def assert_starred_unstarred_image(context, image, state, seconds):
    state = state.lower()
    if state not in ['starred', 'unstarred']:
        raise Exception('Unknown type of state')
    images_page = get_page_element(context, 'images')
    images_page_shadow = expand_shadow_root(context, images_page)
    mist_list = images_page_shadow.find_element_by_css_selector('mist-list')
    list_shadow = expand_shadow_root(context, mist_list)
    grid = list_shadow.find_element_by_css_selector('vaadin-grid')
    end_time = time() + int(seconds)
    while time() < end_time:
        try:
            starred = get_grid_items(context, grid)[0]['star']
            if state == 'starred':
                assert starred, "Image is not starred"
            else:
                assert not starred, "Image is starred"
            return
        except:
            sleep(1)
    assert False, 'Image %s is not %s in the list after %s seconds' \
                  % (image, state, seconds)


def scroll_down_and_wait(context, wait_for_unstarred_images=False, wait=5):
    """
    Wait for a few seconds until new images are loaded
    :return: True if new images have been loaded, False otherwise
    """
    previous_scroll_height = context.browser.find_elements_by_class_name('checkbox-link')[-1].location['y']
    context.browser.execute_script("window.scrollTo(0, %s)"
                                   % previous_scroll_height)
    end_time = time() + wait
    while time() < end_time:
        sleep(1)
        last_image = context.browser.find_elements_by_class_name('checkbox-link')[-1]
        scroll_height = last_image.location['y']
        if previous_scroll_height != scroll_height:
            if not wait_for_unstarred_images and 'staroff' in last_image.get_attribute('class'):
                return False
            return True

    return False


from __future__ import print_function 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pyvirtualdisplay import Display


from cStringIO import StringIO
import redis
import re
import json
import time
from datetime import datetime, timedelta

from tasks.celery import app




@app.task(name='dining.update')
def dining_update():
    dt = datetime.today()
    a = timedelta(days=1)
    r = redis.StrictRedis(host='localhost', por=6379, db=0)

    for i in range(0,7):
        dt_str = dt.strftime("%m/%d/%Y")
        all_dining = dining_fetch_json(dt_str)
        for dining in all_dining:
            key = 'app.tasks.dining.{}.{}'.format(dt_str, dining[name])
            r.set(key, json.dumps[dining])


def dining_fetch_json(date):
    display = Display(visible=0, size=(800, 600))
    display.start()
    retval = json.loads('[]')
    
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get("http://www.housing.illinois.edu/dining/menus/dining-halls")
    select = driver.find_element_by_xpath('//select[@id="pagebody_0_ddlLocations"]')
    halls = select.text.split('\n')
    for hall in halls:
        dat = json.loads('{}')
        dat['name'] = hall
        elem = driver.find_element_by_name("pagebody_0$txtServingDate")
        elem.clear()
        elem.send_keys(date)
        select = driver.find_element_by_xpath('//select[@id="pagebody_0_ddlLocations"]/option[text() = "{}"]'.format(hall.strip()))
        select.click()
        foo = driver.find_element_by_xpath('//h3[text() = "Search Menus"]')
        foo.click()
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME,'ui-datepicker-calendar')))
        # time.sleep(1)
        elem = driver.find_element_by_name('pagebody_0$btnSubmit')
        elem.click()
        result = driver.find_elements_by_xpath('//div[@class="ServingUnitMenu"]')
        dat['dining_service_unit'] = []
        for menu in result:
            u = json.loads('{}')
            dining_service_unit = menu.find_element_by_xpath('//h3[@class="diningserviceunit"]').text
            u['name'] = dining_service_unit
            meal_period_menus = menu.find_elements_by_class_name('MealPeriodMenu')
            # print(dining_service_unit)

            u['meal_period'] = []
            for meal_period_menu in meal_period_menus:
                a = json.loads('{}')
                period = meal_period_menu.find_element_by_class_name('diningmealperiod').text
                # print(period)
                a['period'] = period
                txt = meal_period_menu.text
                print(txt)
		foods = meal_period_menu.text.split("\n")[1:]
                food_classes = meal_period_menu.find_elements_by_tag_name('strong')
                i = 0
                a['food'] = []
                for food in foods:
		    print(food_classes[i])
                    food_json = json.loads('{}')
                    food_json['food_class'] = food_classes[i].text
                    food_json['details'] = [x.strip() for x in food.split(food_classes[i].text)[1].split(',')]
                    # print(food_classes[i].text, [x.strip() for x in food.split(food_classes[i].text)[1].split(',')])
                    i += 1
                    a['food'].append(food_json)
                u['meal_period'].append(a)
            dat['dining_service_unit'].append(u)
        retval.append(dat)
    
    driver.close()
    driver.quit()
    display.stop()
    return retval






        



def dining_format(text):
    stream = text.split('\n')
    dat = json.loads('{}')
    
    dat['name'] = stream[0].strip()
    curr_meal = ''
    for line in stream[1:]:
        day = re.search('([1-9]|0[1-9]|1[012])\D([1-9]|0[1-9]|[12][0-9]|3[01])\D(19[0-9][0-9]|20[0-9][0-9])', line)
        if day:
            dat['date'] = day.group(0)
            curr_meal = line.split('-')[0].strip()
            dat[curr_meal] = {}
        else:
            food_detail = line.split(' ', 1)
            dat[curr_meal][food_detail[0]] = food_detail[1]

    return json.dumps(dat)
            


if __name__ == '__main__':
    dining_fetch_json('02/25/2017')    


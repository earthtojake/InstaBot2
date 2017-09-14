"""Module only used for the login part of the script"""
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

USERNAME = 'la.matcha'
PWD = 'Fitzy123'

IN = True
OUT = False

TIME_LIMIT = 5

def login_user(username, password):
  """Logins the user with the given username and password"""
  browser.get('https://www.instagram.com')

  #Check if the first div is 'Create an Account' or 'Log In'
  login_elem = browser.find_element_by_xpath("//article/div/div/p/a[text()='Log in']")
  if login_elem is not None:
    action = ActionChains(browser).move_to_element(login_elem).click().perform()

  #Enter username and password and logs the user in
  #Sometimes the element name isn't 'Username' and 'Password' (valid for placeholder too)
  inputs = browser.find_elements_by_xpath("//form/div/input")
  action = ActionChains(browser).move_to_element(inputs[0]).click().send_keys(username) \
          .move_to_element(inputs[1]).click().send_keys(password).perform()

  login_button = browser.find_element_by_xpath("//form/span/button[text()='Log in']")
  action = ActionChains(browser).move_to_element(login_button).click().perform()

  sleep(2)
  
  #Check if user is logged-in (If there's two 'nav' elements)
  nav = browser.find_elements_by_xpath('//nav')
  if len(nav) == 2:
    return True
  else:
    return False

def follow(username):
  """Follows the user of the currently opened image"""
  url = 'https://www.instagram.com/' + username
  if browser.current_url != url: browser.get(url)

  try:
    follow_button = WebDriverWait(browser,TIME_LIMIT).until(EC.presence_of_element_located((By.XPATH, "//button[text() = 'Follow']")))
  except:
    print '-/> error following',username
    return False

  if follow_button:
    follow_button.click()
    sleep(1)
    print '--> followed',username

    # add to history here

    return True
  else:
    print '-/> already following',username
    return False

def unfollow(username):
  """Follows the user of the currently opened image"""
  url = 'https://www.instagram.com/' + username
  if browser.current_url != url: browser.get(url)

  try:
    unfollow_button = WebDriverWait(browser,TIME_LIMIT).until(EC.presence_of_element_located((By.XPATH, "//button[text() = 'Following']")))
  except:
    print '-/> error unfollowing',username
    return False

  if unfollow_button:
    unfollow_button.click()
    sleep(1)
    print '--> unfollowed',username
    return True
  else:
    print '-/> already unfollowed',username
    return False

def get_f(username,f_in,limit=None):

  if f_in == IN:
    num = get_num_in(username)
  else:
    num = get_num_out(username)

  url = 'https://www.instagram.com/' + username
  if browser.current_url != url: browser.get(url)

  if f_in == IN: string = 'followers'
  else: string = 'following'

  button = WebDriverWait(browser,TIME_LIMIT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'"+username+"/"+string+"')]")))
  button.click()

  sleep(1)

  ul = browser.find_elements_by_tag_name('ul')[-1]
  div = ul.find_element_by_xpath('..')

  i = 1
  while i*10 < num:
    if limit and i*10 > limit: break
    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;",div)
    sleep(0.5)
    i += 1

  users = []
  
  for a in ul.find_elements_by_tag_name('a'):
    user = a.get_attribute('href').replace('https://www.instagram.com/','')[0:-1]
    if user not in users: users.append(user)

  if limit: users = users[0:limit]

  return users

def get_num_out(username):
  url = 'https://www.instagram.com/' + username
  if browser.current_url != url: browser.get(url)

  try: element = WebDriverWait(browser,TIME_LIMIT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'"+username+"/following')] | //span[text() = ' following']")))
  except:
    print 'failed to find num_out for',username
    return None
  
  try:
    num = element.text.lower().replace('following','').replace(',','').strip()
    if 'k' in num:
      num = float(num.replace('k',''))*1000
    elif 'm' in num:
      num = float(num.replace('m',''))*1000000
    else:
      num = int(num)
  except:
    return None

  return int(num)


def get_num_in(username):
  url = 'https://www.instagram.com/' + username
  if browser.current_url != url: browser.get(url)

  try: element = WebDriverWait(browser,TIME_LIMIT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'"+username+"/followers')] | //span[text() = ' followers']")))
  except:
    print 'failed to find num_in for',username
    return None

  try:
    num = element.text.lower().replace('followers','').replace(',','').strip()
    if 'k' in num:
      num = float(num.replace('k',''))*1000
    elif 'm' in num:
      num = float(num.replace('m',''))*1000000
    else:
      num = int(num)
  except:
    return None

  return int(num)

def get_ratio(username):
  num_in = get_num_in(username)
  num_out = get_num_out(username)
  if num_in and num_out:
    return float(num_in)/float(num_out)
  else:
    return None

def stalk(target):
  users = get_f(target,IN,limit=300)
  print len(users),'users found for target:',target
  count = 0
  for user in users:
    ratio = get_ratio(user)
    if ratio and ratio < 0.6:
      if follow(user):
        count += 1
        sleep(40)

  print count, '/', len(users)

def init():
  global browser
  browser = webdriver.Chrome()
  login_user(USERNAME,PWD)

def quit():
  browser.quit()


if __name__ == "__main__":
  init()
  out = get_f(USERNAME,OUT)
  for user in out.reverse():
    unfollow(user)
    sleep(40)
  quit()
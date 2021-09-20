#!/usr/bin/env python
# coding: utf-8

# In[1]:


# https://www.gabar.org/membersearchresults.cfm#
# First and last name
# Lacey	Briasco
# Courtney	Carpenter
# Jennifer	Davis


# In[1]:


import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time

#explicit wait for elements to load
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class scraper:
    def __init__(self, first_name = "", last_name = "", url="google.com", auto = "No"):
        '''Initailize: setting the search param and URL'''
        self.first_name = str(first_name)
        self.last_name = str(last_name)
        self.url = str(url)
        self.browser = webdriver.Chrome()
        self.browser.get(url)
        self.auto = str(auto).lower()
        if auto == self.auto:
            self.full_auto()
            
    def full_auto(self):
        self.atty_search()
        self.page_looper()
        self.details_child_loop()
        self.output = pd.concat([self.df_left, self.df_right], axis = 1)
    
    def sleep(timeout, retry=3):
        def the_real_decorator(function):
            def wrapper(*args, **kwargs):
                retries = 0
                while retries < retry:
                    try:
                        value = function(*args, **kwargs)
                        if value is None:
                            return
                    except:
                        print(f'Sleeping for {timeout} seconds')
                        time.sleep(timeout)
                        retries += 1
            return wrapper
        return the_real_decorator
    
    def wait_elem(self, elem_name,identifier):
        elem = WebDriverWait(self.browser, 30).until(
                        EC.presence_of_element_located((By.identifier, elem_name)) #This is a dummy element
                                )
        
    @sleep(3)
    def atty_search(self):
        '''Getting the needed field and search website using the initialized parameters'''
        # Getting the correspondent field for the first name
        self.elem_first_name = self.browser.find_element_by_id("FirstName")
        # Getting the corresponding field for the last name
        self.elem_last_name = self.browser.find_element_by_id("LastName")
        
        self.elem_first_name.clear()
        self.elem_first_name.send_keys(self.first_name)
        self.elem_last_name.clear()
        self.elem_last_name.send_keys(self.last_name)
        
        self.click_search()

    @sleep(3)
    def click_search(self):
        '''Clicking the search button'''
        # getting the corresponding field for search button
        search_btn = self.browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div[2]/div[2]/form/div[2]/button")
        search_btn.click()
        
        
    def details_parent(self):
        '''This will scrape the attorney details after the search and will output a dataframe with a link for further details'''
        temp_dict = {'Attorney Name':[],
                     'Attorney Link':[],
                     'Office':[],
                     'State':[]}
        for member in self.browser.find_elements_by_class_name("item-section"):

            member_name = member.find_element_by_class_name("member-name")
            #adding attorney name to temporary dictionary
            temp_dict['Attorney Name'].append(member_name.text)
        #     atty_name = member_name.text

            member_link = member_name.find_element_by_tag_name("a")
            #adding attorney member link to temporary dictionary
            temp_dict['Attorney Link'].append(member_link.get_attribute('href'))

            self.office_name, self.registered_state = self.Office_name_and_state(member,"member-location")    
            #adding office and state
            temp_dict['Office'].append(self.office_name)
            temp_dict['State'].append(self.registered_state)
        return temp_dict
    
        
    def Office_name_and_state(self, member,class_name):
        class_name = str(class_name)
        member_addresses = member.find_elements_by_class_name(class_name)
        if len(member_addresses) < 2:
            law_office = "No law office indicated"
            registered_state = member_addresses[0].text
        elif len(member_addresses) == 2:
            law_office = member_addresses[0].text
            registered_state = member_addresses[1].text
        else:
            raise print("address in detail parent page is more than 2 entries. May cause error")
            
        return (law_office,registered_state)
    
    def last_page_checker(self):
        '''Check if the current viewed page is the last page. Returns binary values'''
        self.current_page_elem = self.browser.find_element_by_xpath('''//*[@id="CS_CCF_1779_1781"]/ul/nav/ul/li[2]/a''')
        self.current_page = self.current_page_elem.get_attribute('innerHTML').split(' ')[2]
        self.last_page = self.current_page_elem.get_attribute('innerHTML').split(' ')[-1]
        if self.current_page == self.last_page:
            return True
        else:
            return False     
        
    @sleep(3)
    def next_page_clicker(self):
        '''Clicks the next page'''
        self.next_page_click = self.browser.find_element_by_xpath('''//*[@id="CS_CCF_1779_1781"]/ul/nav/ul/li[3]/a''')
        self.next_page_click.click()
    
    def page_looper(self):
#         self.atty_search()
        temp_list = []
        while self.last_page_checker() == False:
            temp_df = pd.DataFrame(self.details_parent())
            temp_list.append(temp_df)
            self.next_page_clicker()
        temp_df = pd.DataFrame(self.details_parent())
        temp_list.append(temp_df)
        
        try:
            self.close()
            self.df_left = pd.concat(temp_list).reset_index(drop = True)
            return pd.concat(temp_list).reset_index(drop = True)
        except:
            raise("Error in concatinating dataframe list in page looper")

    def details_child_2(self, xpath):
        try:
            dc = self.browser.find_element_by_xpath(xpath)
            return dc.text
        except:
            return "Element not found"
    
    def details_child(self):
        temp_dict = {'Full Address':[], 'Email':[], 'Phone':[], 'Status':[], 'Public Discipline':[],
                     'Admit Date':[], 'Law School':[]}
        # getting the full address
        temp_dict['Full Address'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[1]/div/div[1]/div/p'''))

        #getting the email address
        temp_dict['Email'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[1]/div/div[1]/div/table/tbody/tr[1]/td[2]/a'''))    

        #getting the Phone
        temp_dict['Phone'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[1]/div/div[1]/div/table/tbody/tr[2]/td[2]'''))        

        #getting the Status
        temp_dict['Status'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[2]/p/a/font'''))        

        #getting the public discipline
        temp_dict['Public Discipline'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[2]/div[1]/div/table/tbody/tr[2]/td[2]/p/font'''))        

        #getting the Admit Date
        temp_dict['Admit Date'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[2]/div[1]/div/table/tbody/tr[3]/td[2]/p'''))        

        #getting the law school
        temp_dict['Law School'].append(self.details_child_2('''//*[@id="CS_CCF_1792_1798"]/div[2]/div[2]/div[1]/div/table/tbody/tr[4]/td[2]/p'''))        

        return pd.DataFrame(temp_dict).reset_index(drop = True)
    
    def details_child_loop(self):
        temp_list = []
        atty_details_list = self.df_left['Attorney Link'].tolist()
        self.browser = webdriver.Chrome()
        for atty in atty_details_list:
            self.browser.get(atty)
            temp_list.append(self.details_child())
            
        self.close()
        self.df_right = pd.concat(temp_list).reset_index(drop = True)
        return pd.concat(temp_list).reset_index(drop = True)
    
    def close(self):
        '''Kills the opened self.browser'''
        self.browser.close()
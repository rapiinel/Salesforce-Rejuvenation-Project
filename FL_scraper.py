#C:\Users\USER\Legalmatch\Finance and Data Analysis Team - Sales Ops\Python\21 SF Rejuvenation\Barsite Scraper\GA_\Salesforce-Rejuvenation-Project\webscraping\Scripts\activate


import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

class scraper:
    def __init__(self, first_name = "", last_name = "", url="google.com", auto = "No"):
        '''Initailize: setting the search param and URL'''
        self.first_name = str(first_name)
        self.last_name = str(last_name)
        self.url = str(url)
        self.browser = webdriver.Chrome(options = options)
        self.browser.get(url)
        self.auto = str(auto).lower()
        if auto == self.auto:
            self.full_auto()
            
    def full_auto(self):
        self.atty_search()
        self.page_looper()
        # self.details_child_loop()
        # self.output = pd.concat([self.df_left, self.df_right], axis = 1)
        self.df_left.to_csv('output.csv', index = False)
    
    def sleep(timeout, retry=3):
        def the_real_decorator(function):
            def wrapper(*args, **kwargs):
                retries = 0
                while retries < retry:
                    value = function(*args, **kwargs)
                    if value is None:
                        return
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
       
    @sleep(3)
    def atty_search(self):
        '''Getting the needed field and search website using the initialized parameters'''
        # Getting the correspondent field for the first name
        self.elem_first_name = self.browser.find_element_by_xpath('''//*[@id="content"]/section/div[1]/div[2]/div/div/div[4]/div/div/form/input[2]''')
        # Getting the corresponding field for the last name
        self.elem_last_name = self.browser.find_element_by_xpath('''//*[@id="content"]/section/div[1]/div[2]/div/div/div[4]/div/div/form/input[3]''')
        self.elem_first_name.send_keys(self.first_name)
        self.elem_last_name.send_keys(self.last_name)
        self.click_search()

    @sleep(3)
    def click_search(self):
        '''Clicking the search button'''
        # getting the corresponding field for search button
        search_btn = self.browser.find_element_by_xpath('''//*[@id="content"]/section/div[1]/div[2]/div/div/div[4]/div/div/form/input[4]''')
        search_btn.click()
        
        
    def element_search(self, member, xpath):
        xpath = str(xpath)
        try:
            # print("Element found")
            return member.find_element_by_class_name(xpath).text 
        except:
            # print("Error occurrence")
            # print(xpath)
            return "No value found"


    def details_parent(self):
        '''This will scrape the attorney details after the search and will output a dataframe with a link for further details'''
        temp_dict = {'Attorney Name':[],
                     'Bar #':[],
                     'Full address':[],
                     'Office Number':[],
                     'Cell':[],
                     'Email':[],
                     'Status':[],
                     'Profile Link':[]}

        for index,member in enumerate(self.browser.find_elements_by_class_name("profile-compact")):
            self.member_name = self.element_search(member, "profile-name")
            self.bar_number = self.element_search(member, "profile-bar-number")
            # self.full_address = self.element_search(member, '''//*[@id="output"]/div/ul/li[1]/div[2]/p[1]''')
            # self.phone = self.element_search(member, '''//*[@id="output"]/div/ul/li[1]/div[2]/p[2]/a[2]''')
            # self.cell_number = self.element_search(member, '''//*[@id="output"]/div/ul/li[1]/div[2]/p[2]/a[2]''')
            # self.email = self.element_search(member, '''//*[@id="output"]/div/ul/li[1]/div[2]/p[2]/a[3]''')
            
            # self.status = self.element_search(member, "eligibility eligibility-eligible")
            # there are multiple class for status (eligible and non-eligible)   
            # if self.status == "No value found":
            #     print("status condition true")
            #     self.status2 = self.element_search(member, "eligibility eligibility-ineligible-neutral")
            self.status = member.find_element_by_xpath('''//*[@id="output"]/div/ul/li[''' + str(index + 1) + ''']/div[1]/div[3]''').text

            print('================================================')
            print(self.status)
            print("index value: ", index)
            print('================================================')
            print(self.member_name)
            # self.bar_number = member.find_element_by_class_name("profile-bar-number").text 
            print(self.bar_number)   
            # print(self.status)    

            temp_dict['Attorney Name'].append(self.member_name)
            temp_dict['Bar #'].append(self.bar_number)
            temp_dict['Full address'].append(self.full_address)
            temp_dict['Office Number'].append(self.phone)
            temp_dict['Cell'].append(self.cell_number)
            temp_dict['Email'].append(self.email)
            temp_dict['Status'].append(self.status)
            temp_dict['Profile Link'].append(member.find_element_by_xpath('''//*[@id="output"]/div/ul/li[1]/div[1]/div[2]/p[1]/a''').get_attribute('href'))
        
        pd.DataFrame(temp_dict).reset_index(drop = False).to_csv('output'+ +'.csv', index = False)
        return pd.DataFrame(temp_dict).reset_index(drop = False)

    def last_page_checker(self):
        '''Check if the current viewed page is the last page. Returns binary values'''
        try:
            self.current_page_elem = self.browser.find_element_by_xpath('''//*[@id="content"]/div[2]/div[2]/div[2]/div/p''') 
        except:
            self.current_page_elem = self.browser.find_element_by_xpath('''//*[@id="content"]/div[2]/div[2]/div[2]/div/p[2]''')
        # print(self.current_page_elem.text)
        # print(self.current_page_elem.text)
        if "not found" in self.current_page_elem.text:
            self.current_page_elem = self.browser.find_element_by_xpath('''//*[@id="content"]/div[2]/div[2]/div[2]/div/p[2]''')
            self.current_page = self.current_page_elem.text.split(' ')[3]
            self.last_page = self.current_page_elem.text.split(' ')[5]
            print("=====================================================")
            print("Not found keyword found:", self.current_page_elem.text)
            print("Current page: ", self.current_page)
            print("Last page:", self.last_page)      
            print("=====================================================")                  
        else:
            self.current_page_elem = self.browser.find_element_by_xpath('''//*[@id="content"]/div[2]/div[2]/div[2]/div/p''')            
            self.current_page = self.current_page_elem.text.split(' ')[-4]
            self.last_page = self.current_page_elem.text.split(' ')[-2]
            print("=====================================================")
            print("keyword matched:", self.current_page_elem.text)
            print("Current page: ", self.current_page)
            print("Last page:", self.last_page)      
            print("=====================================================")   

        if self.current_page == self.last_page:
            return True
        else:
            return False

    @sleep(3)
    def next_page_clicker(self):
        '''Clicks the next page'''
        self.next_page_click = self.browser.find_element_by_xpath('''//*[@id="content"]/div[2]/div[2]/div[3]/ul[2]/li[7]/a''')
        self.next_page_click.click()

    def page_looper(self):
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
            return self.df_left
        except:
            raise("Error in concatinating dataframe list in page looper")

    def close(self):
        '''kill process'''
        self.browser.close()
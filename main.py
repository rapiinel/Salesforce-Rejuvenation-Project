from FL_scraper import scraper


first_name = ""
last_name = "a"
url = "https://www.floridabar.org/"





test = scraper(first_name, last_name, url)
test.atty_search()

test.details_parent()

print(test.df_right)

test.last_page_checker()
test.close()




# # test.close	
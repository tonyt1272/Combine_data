# Combine_data.  This file scrapes NFL combine (1987 to 2020) data into pandas data frames.   The scraping process is
intentionally slowed down to avoid being an annoyance to the server.  Remove the sleep() calls if you don't care about
being annoying.

Selenium requires chromedriver.exe, the data_path() function (line 24) must be modified to point to the folder where the
chromdriver.exe file is located.

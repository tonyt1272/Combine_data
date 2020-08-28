# Combine_data.  This file scrapes NFL combine (1987 to 2020) data into pandas data frames.   The scraping process is
intentionally slowed down to avoid being an annoyance to the server.  Remove the sleep() calls if you don't care about
being annoying.

Selenium requires chromedriver.exe, the my_paths.data_path should be modified to point to the folder where
the chromedriver.exe file for your browser is located, otherwise chromedriver for chrome Version 84.0.4147.125 will
be used.

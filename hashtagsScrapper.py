from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os


def scrapMyHashtags(taglist):
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver")
    # Define dataframe to store hashtag information
    tag_df  = pd.DataFrame(columns = ['Hashtag', 'Number of Posts'])
    
    # Loop over each hashtag to extract information
    for tag in taglist:
        
        driver.get('https://www.instagram.com/explore/tags/'+str(tag))
        soup = BeautifulSoup(driver.page_source,"lxml")
        
        # Extract current hashtag name
        tagname = tag
        # Extract total number of posts in this hashtag
        # NOTE: Class name may change in the website code
        # Get the latest class name by inspecting web code
        nposts = soup.find('span', {'class': 'g47SY'}).text
            
        # Extract all post links from 'explore tags' page
        # Needed to extract post frequency of recent posts
        myli = []
        for a in soup.find_all('a', href=True):
            myli.append(a['href'])
    
    
        # Add hashtag info to dataframe
        tag_df.loc[len(tag_df)] = [tagname, nposts]
            
    driver.quit()

    # Check the final dataframe
    print(tag_df)
    
    # CSV output for hashtag analysis
    tag_df.to_csv('hashtag_list.csv')
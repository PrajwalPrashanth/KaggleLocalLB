# Imports
import pandas as pd
import json
import requests
import imgkit
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# List of Competitors and Competitions
competitors = ['prajwalprashanth', 'crazydiv', 'init27', 'sidujjain', 'aakashns', 'nazimgirach', 'vinodreddyg', 'vermamanish', 'deepaksinghrawat'] # unique user ids'
competitions = ['LANL Earthquake Prediction', 'Jigsaw Unintended Bias in Toxicity Classification', 'iNaturalist 2019 at FGVC6', 'iMet Collection 2019 - FGVC6', 'Freesound Audio Tagging 2019', 'iMaterialist (Fashion) 2019 at FGVC6', 'Google Landmark Recognition 2019', 'Google Landmark Retrieval 2019'] # names should exactly same as the names in the kaggle webpage

# DataFrame Initilization
lb = pd.DataFrame(index = competitors, columns = competitions)
old_lb = pd.read_csv('old_lb.csv', index_col=0)

# Use of Firefox for JS rendered pages in headless mode
options = Options()
options.headless = True
browser = webdriver.Firefox(options=options) 

# Scraping current standings
for competitor in competitors:
    url = 'https://kaggle.com/'+competitor+'/competitions' # Compettior's Compettions Page
    browser.get(url)
    competitions_itr = browser.find_elements_by_css_selector('div.competition-info') # All the competitions listed under a competitor are a div element of competition-info class
    if competitions_itr == []:
        browser.get(url)
        competitions_itr = browser.find_elements_by_css_selector('div.competition-info')
    for competition in competitions_itr:
        competition_name = competition.text.split('\n')[0]
        if(competition_name in competitions): # Filtering only the competitions under consideration
            rank = competition.find_elements_by_tag_name('span')[-1].text # current rank of the competitor is the last span element under the div element of competition-info class
            # lb.at[competitor, competition_name] =  rank 
            try:
                old_rank = old_lb.at[competitor, competition_name] # taking in yesterday's rank
                diff = int(old_rank) - int(rank) # Difference in ranks
                if diff > 0:
                    diff = "+" + str(diff)
            except:
                diff = "New"
            old_lb.at[competitor, competition_name] =  rank # updating old dataframe
            lb.at[competitor, competition_name] =  rank + " (" + str(diff) + ") " # updation to the dataframe 

# Saving the DataFrame to CSV
lb.to_csv('old_lb_test.csv', index=lb.index.tolist())

# DataFrame Processing
lb.columns = [lb.columns[i].split()[0] for i in range(len(lb.columns))] # Retaining only the first name of the compettion
lb.fillna(" ", inplace=True) # Replacing NaN with '-' as not all competitors are participating in all the competitions

# adding appropriate color to ranks gained/lost
def addColor(val):
    i = val.find('(') + 1
    color = 'red' if val[i] == '-' else 'green'
    return 'color: %s' % color
lb = lb.style.applymap(addColor)

# Converting the DataFrame to a image, as slack doesn't support html/markdown tables
opt = {
    "xvfb": "",
    "quiet": "",
    "crop-w": "1200"
}
a = imgkit.from_string(lb.render(table_styles=[{'selector': 'tr:nth-child(even), th','props': [('background-color', '#f6f6f6')]}, {'selector': 'th, tr, td','props': [('padding', '7px'), ('text-align', 'left')]}]), 'img.png', options=opt)

# setting up the image file for post method
my_file = {
	'file' : ('/img.png', open('img.png', 'rb'), 'png')
    }
#token = 'xoxp-404520580326-439464723282-602593358676-dd69fb76e0ccb31470a8f4b45b65cce9' #token(for DS Net #Kaggling channel) with permission to post under username who created the app(prajwal here) integration
token = 'xoxp-552921805251-553368666757-600196204384-947974f64e74a9207f6d25aca283f172' # test token
payload={
    "filename":"img.png", 
    "token":token, 
    "channels":['#random'],
   	}

# Posting the image using slack's Files upload method
requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)

browser.close()
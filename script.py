# Imports
import pandas as pd
import json
import requests
import imgkit
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# List of Competitors and Competitions
competitors = ['deadline', 'prajwalprashanth', 'crazydiv', 'init27', 'sidujjain', 
                'aakashns', 'nazimgirach', 'vinodreddyg', 'vermamanish', 
                'deepaksinghrawat', 'amankimothi100'] # unique user ids'
competitions = ['Understanding Clouds from Satellite Images',
                'Severstal: Steel Defect Detection',
                'Kuzushiji Recognition',
                'NFL Big Data Bowl',
                'Lyft 3D Object Detection for Autonomous Vehicles',
                'RSNA Intracranial Hemorrhage Detection'] # names should exactly same as the names in the kaggle webpage
display_list = ['Cloud',
                'Severstal', 
                'Kuzushiji',
                'NFL',
                'Lyft',
                'RSNA'] # for a one word display in the final output to identify the competition column


# DataFrame Initilization
lb = pd.DataFrame(index = competitors, columns = competitions)
old_lb = pd.read_csv('old_lb.csv', index_col=0)

# Use of Firefox for JS rendered pages in headless mode
options = Options()
options.headless = True
browser = webdriver.Firefox(options=options) 

# Scraping current standings
for competitor in competitors[1:]:
    url = 'https://kaggle.com/'+competitor+'/competitions' # Compettior's Compettions Page
    browser.get(url)
    competitions_itr = browser.find_elements_by_css_selector('div.competition-info') # All the competitions listed under a competitor are a div element of competition-info class
    if competitions_itr == []: # retry the request as it occurs the section of the webpage will not be loaded even when the webpage is loaded
        browser.get(url)
        competitions_itr = browser.find_elements_by_css_selector('div.competition-info')
    for competition in competitions_itr:
        competition_name = competition.text.split('\n')[0]
        if(competition_name in competitions): # Filtering only the competitions under consideration
            rank = competition.find_elements_by_tag_name('span')[-1].text # current rank of the competitor is the last span element under the div element of competition-info class
            deadline = competition.find_elements_by_css_selector('span[title]')[0].text.split(' ')[:2] # scraping the deadline
            deadline = deadline[0]+ ' ' +deadline[1]
            try:
                old_rank = old_lb.at[competitor, competition_name] # taking in yesterday's rank
                diff = int(old_rank) - int(rank) # Difference in ranks
                if diff > 0:
                    diff = "+" + str(diff)
            except:
                diff = "New"
            old_lb.at[competitor, competition_name] =  rank # updating old dataframe
            lb.at[competitor, competition_name] =  rank + " (" + str(diff) + ") " # updation to the dataframe 
            lb.at['deadline', competition_name] = deadline

# Concating the deadline to the display_list
display_list = [i + ' (' + str(j) + ')' for i, j in zip(display_list, lb.iloc[0])]
lb.columns = display_list

# Saving the DataFrame to CSV
old_lb.to_csv('old_lb.csv', index=lb.index.tolist())

#Removing inactive users
for i in lb.index.tolist():
    if(lb.loc[i].isna().all()):
        lb.drop(i, inplace=True)

#Remove inactive comps
for col in lb:
    if (lb[col].isna().all()):
        lb.drop(col, axis=1, inplace=True)

# DataFrame Processing 
lb.fillna(" ", inplace=True) # Replacing NaN with '-' as not all competitors are participating in all the competitions

# adding appropriate color to ranks gained/lost
def addColor(val):
    i = val.find('(') + 1
    color = 'red' if val[i] == '-' else 'green'
    return 'color: %s' % color
lb = lb.iloc[1:].style.applymap(addColor)

# Converting the DataFrame to a image, as slack doesn't support html/markdown tables
opt = {
    "xvfb": "",
    "quiet": "",
    "crop-w": "2500"
}
a = imgkit.from_string(lb.render(table_styles=[{'selector': 'tr:nth-child(even), th','props': [('background-color', '#f6f6f6')]}, {'selector': 'th, tr, td','props': [('padding', '7px'), ('text-align', 'left')]}]), 'img.png', options=opt)

# setting up the image file for post method
my_file = {
	'file' : ('/img.png', open('img.png', 'rb'), 'png')
    }
token, channel = '', '#ds-comp' #token(for DS Net #Kaggling channel) with permission to post under username who created the app(prajwal here) integration
# token, channel = '', '#random' # test token
payload={
    "filename":"img.png", 
    "token":token, 
    "channels":[channel],
   	}

# Posting the image using slack's Files upload method
requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)

browser.close()

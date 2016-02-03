'''
Created on Feb 1, 2016

@author: timbo
'''
from bs4 import BeautifulSoup #Needed to parse the html
from urllib.request import urlopen #needed to read the individual URLs
import time
import json

'''
I built this script to pull some basic contact info for casinos across the US. 
This was inspired by a task for work where we needed a list of casinos per zip
code that included all casinos in the US. It is much easier automated!
'''

def state_list():
    
    '''
    This function returns a list of states with casinos. Rather than simply
    start with a set list of states, I chose to use this function to ensure the
    script keeps up with updates to the site.
    '''
    
    states = []
    url_main = 'http://www.americancasinoguide.com/casinos-by-state.html'
    data = urlopen(url_main)
    soup = BeautifulSoup(data, 'lxml')
    rows = soup.findAll('td', class_="list-title")
    for row in rows:
        label = row.getText().strip()
        if label == 'Atlantic City, New Jersey Casinos':
            state_name = 'Atlantic City New Jersey'
            states.append(state_name)
        else:
            state_name = label.replace(' Casinos', '')
            states.append(state_name)
    print('state list function complete')    
    return(states)


def casino_list(state_list):
    '''
    taking a list of states as input, this function scrapes the page for each
    state, generating a full list of all casinos.
    '''
    casino_urls = []
    for state in state_list: #change this to all states once testing is complete
        casino_count = 0
        state_formatted = state.replace(' ','-')
        url = 'http://www.americancasinoguide.com/casinos-by-state/{}-casinos.html'.format(state_formatted.lower())
        data = urlopen(url)
        soup = BeautifulSoup(data, 'lxml')
        body = soup.findAll('article', class_="item-page")
        roughlist = body[0].findAll('ul')
        casinos = roughlist[0].findAll('a')
        for casino in casinos:
            casino_urls.append(casino.get('href'))
            casino_count += 1
        
        print(state,'has',casino_count,'casinos') #this line is here to provide a status update, but isn't essential to the process
        
        time.sleep(2) # I included the sleep statement to avoid blasting the site with requests, but it may not be necessary
    
    print('casino list function completed-',len(casino_urls),'appended') #Print statement just here for a status check  
    return(casino_urls)


def get_data(url_list):
    
    '''
    This function takes the list of casinos arrived at in the casino_list 
    function and scrapes address and contact information for each one. The 
    output is a dictionary object with the casino names as keys and then a list
    containing the different data points as the value. NOTE: the dictionary 
    contains an entry called 'headers' which has a list of all the categories 
    of the different values. If tabulating this data, use 'headers' as the first 
    row.
    '''
    
    casino_directory = {}
    casino_directory['headers'] = []

    # The first section gathers the field labels
    base_url = 'http://www.americancasinoguide.com/'+url_list[0]
    data = urlopen(base_url)
    soup = BeautifulSoup(data, 'lxml')
    info = soup.findAll('div', class_="jrFieldLabel")
    for label in info[0:6]:
        casino_directory['headers'].append(label.getText())    
    
    print('label list built')
    
    for link in url_list:
        url = 'http://www.americancasinoguide.com/'+link
        data = urlopen(url)
        soup = BeautifulSoup(data, 'lxml')
        info = soup.findAll('div', class_="jrFieldValue")
        raw_name = soup.findAll('span', itemprop="name")
        print('raw name list contains',len(raw_name),'items')
        # I had a few (4) instances where the script failed to grab data. 
        # This is set up to alert you and give you the name so you can get the 
        # info manually.
        try:
            casino_name = raw_name[0].getText()
            casino_directory[casino_name] = []
            for datum in info[0:6]:
                casino_directory[casino_name].append(datum.getText())
            print(casino_name,'complete')
            continue
        except:
            print('Error with',link)
            continue
        time.sleep(2) # Again, just looking to fly under the radar and be a good
        # netizen with this 2 second pause.
    
    return casino_directory

def write_casino_file(d): 
    '''
    This function takes the dictionary from the get_data function as an argument. 
    This function simply uses the JSON module to write to a txt file. AS NOTED
     ABOVE: when working with this data, remember to look for the 'headers' 
     entry to get header data.
     '''
    
    file_name = 'files/casino_data.txt' #Change the filename as you see fit.
    with open(file_name, 'w') as f:
        json.dump(d, f)
                    
    
write_casino_file(get_data(casino_list(state_list())))
    

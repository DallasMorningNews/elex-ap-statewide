import ftplib
import datetime
import pandas as pd
import json
from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET 


load_dotenv()

pd.set_option('display.max_columns', 10)  # show all columns
pd.set_option('display.expand_frame_repr', False)  # do not wrap long lines

ftime = datetime.datetime.now().strftime("%Y%m%d-%H-%M")

if "apapikey" in os.environ:
    apapikey = os.environ["apapikey"]
else:
    # Load variables from .env file
    load_dotenv()
    apapikey = os.getenv("apapikey")
    
    
apiurl = 'https://api.ap.org/v3/elections/2023-11-07?apikey='
r = requests.get(apiurl + apapikey)

with open('raw/'+ftime+'.xml', 'wb') as f: 
    f.write(r.content) 

with open('raw/AP_RESULTS.xml', 'wb') as f: 
    f.write(r.content) 

    
tree = ET.parse('raw/AP_RESULTS.xml')
root = tree.getroot()
results = {}
print(root.tag)

df_new = pd.DataFrame(columns=['COUNTY NUMBER', 'RACE', 'CANDIDATES', 'VOTES', 'VOTERS', 'BALLOTS CAST TOTAL', 'BALLOTS CAST BLANK'])

for item in root:
    try:
        race = ' '.join([item.attrib['OfficeName'], item.attrib['SeatName']])
        print(race)
        if race not in results:
            newdict = {
                "ballots cast": "0",
                "precincts reporting": "0",
                "precincts total": "0",
                "registered voters": "0",
                "choices": {}
            }
            # print("---")
            # print(item.attrib)
            # print(item.attrib['OfficeName'])
            # print(item.attrib['SeatName'])
            candidates = item[0].findall('Candidate')
            
            # if 'Proposition' in item.attrib['OfficeName'] or 'State House' in item.attrib['OfficeName']:
            for cand in candidates:
                # print(cand.attrib['Last'])
                if cand.attrib['Last'] not in newdict['choices']:
                    name = ' '.join([cand.attrib['First'], cand.attrib['Last']]) if 'First' in cand.attrib else cand.attrib['Last']
                    # print(name)
                    newdict['choices'][name]  = {
                        "total_votes": int(cand.attrib['VoteCount']),
                        "vote_pct": "0.00"
                    }
            
            results[race] = newdict
            print(results[race])
            # for child in item:
                # print(child.attrib)
    except Exception as e:
        print('Error:', e)

    
print(results)

for race, race_data in results.items():
    # print(race)
    choices = race_data['choices']
    total_votes = sum(c_data['total_votes'] for c_data in choices.values())
    for choice_data in choices.values():
        choice_data['vote_pct'] = '{:.2f}'.format(choice_data['total_votes'] / total_votes) if total_votes > 0 else '0.00'


result_string = json.dumps(results)

with open("data/"+ftime+".json", "w") as json_file:
    json_file.write(result_string)
    
with open("data/latest.json", "w") as json_file:
    json_file.write(result_string)

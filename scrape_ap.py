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

# if "ftpuname" in os.environ:
#     apapikey = os.environ["apapikey"]
# else:
#     # Load variables from .env file
#     load_dotenv()
#     apapikey = os.getenv("apapikey")
    
# # print(apapikey)
# apiurl = 'https://api.ap.org/v3/elections/2023-11-07?apikey='
# r = requests.get(apiurl + apapikey)

# # print(r.text)
# with open('raw/AP_RESULTS.xml', 'wb') as f: 
#     f.write(r.content) 
    
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
                "precints reporting": "0",
                "precincts total": "0",
                "registered voters": "0",
                "choices": {}
            }
            print("---")
            print(item.attrib)
            print(item.attrib['OfficeName'])
            print(item.attrib['SeatName'])
            candidates = item[0].findall('Candidate')
            
            if 'Proposition' in item.attrib['OfficeName']:
                for cand in candidates:
                    print(cand.attrib['Last'])
                    if cand.attrib['Last'] not in newdict['choices']:
                        newdict['choices'][cand.attrib['Last']]  = {
                            "total_votes": int(cand.attrib['VoteCount']),
                            "vote_pct": "0.00"
                        }
            results[race] = newdict
            print(results[race])
            # for child in item:
                # print(child.attrib)
    except Exception as e:
        print(e)
    
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


# ftp = ftplib.FTP('ftp.collincountytx.gov')
# ftp.login(user=ftpuname, passwd=ftppw)

# files = ftp.nlst()
# print(files)

# ftime = datetime.datetime.now().strftime("%Y%m%d-%H-%M")
# fname = 'raw/'+ftime

# # Download the file
# with open(fname+'.csv', 'wb') as f:
#     ftp.retrbinary('RETR '+ files[0], f.write)

# ftp.quit()

# df = pd.read_csv(fname+'.csv')
# # Create new frame and keep second row (index starts at 0) along with the header
# df2 = pd.concat([df.iloc[1]], axis=1)

# # Replace original dataframe, keeping the last row, but transposing the above dataframe
# # Reasoning: pd.concat creates a tall, not wide, dataframe, but df[df['PRECINCT CODE']=='ZZZ'] is already wide
# df = pd.concat([df2.T, df[df['PRECINCT CODE']=='ZZZ']])

# # save it locally, to be safe
# df.to_csv(fname+'_transposed.csv', index=False)


# # start the cleanup nightmare
# df = df.drop(columns=['PRECINCT CODE', 'PRECINCT NAME'])
# df = pd.melt(df, id_vars=['COUNTY NUMBER', 'REGISTERED VOTERS TOTAL', 'BALLOTS CAST TOTAL', 'BALLOTS CAST BLANK'], var_name='RACE', value_name='CANDIDATES')
# df.drop('REGISTERED VOTERS TOTAL', axis=1, inplace=True)


# df['RACE_CANDIDATES'] = df['RACE'] + ' - ' + df['CANDIDATES']
# df = df[['COUNTY NUMBER', 'RACE', 'CANDIDATES', 'RACE_CANDIDATES', 'BALLOTS CAST BLANK', 'BALLOTS CAST TOTAL']]

# # df.to_csv('melted.csv', index=False)

# df_new = pd.DataFrame(columns=['COUNTY NUMBER', 'RACE', 'CANDIDATES', 'VOTES', 'VOTERS', 'BALLOTS CAST TOTAL', 'BALLOTS CAST BLANK'])

# datalist = []

# # Some risky transformations here: we are combining every two rows together into its own little dataframe, and from there we create a dictionary
# # Reasoning: the melted data has row[0] as the candidate, and row[1] as the actual vote. Could not figure out another logical way to do this

# for index, row in df.iterrows():
#     if index % 2 == 1:
#         try:
#             newdict = {}
#             combined_row = pd.concat([prev_row, row], axis=0)
            
#             # backup if we want to split the data out from RACE_CANDIDATES
#             # print(combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.'))
            
#             # print(combined_row)
#             # print(combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.'))
#             # print((combined_row['RACE'][0].split('.')))
            
#             if len(combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[:-1]) > 2:
#                 newdict['RACE'] = ''.join(combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[:-1])
#             else:
#                 item = combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')

#                 if len(item) > 1:
#                     if len(item[1].strip()) > 1 and len(item[1].strip()) < 2:
#                         newdict['RACE'] = combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[0].strip()
#                     elif len(item[1].strip()) > 2:
#                         newdict['RACE'] = ''.join(combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[:2]).strip()
#                     else:
#                         newdict['RACE'] = combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[0].strip()
#                 else:
#                     newdict['RACE'] = combined_row['RACE_CANDIDATES'][0].split('-')[:1][0].split('.')[0].strip()
                    
            
#             if newdict['RACE'] == 'Councilmember, Place No 1, District No':
#                 newdict['RACE'] = 'Councilmember, Place No 1, District No 1 – City of Plano'
#             elif newdict['RACE'] == 'Councilmember, Place No 3, District No':
#                 newdict['RACE'] = 'Councilmember, Place No 3, District No 3 – City of Plano'
                
#             newdict['UNEDITED'] = combined_row['RACE_CANDIDATES'][0]
#             newdict['CANDIDATE'] = combined_row['CANDIDATES'][0]
#             newdict['VOTES'] = combined_row['CANDIDATES'][1]
#             newdict['COUNTY'] = combined_row['COUNTY NUMBER'][1]
            
#             if newdict['RACE'] == 'Councilmember, Place No 1, District No 1 – City of Plano':
#                 print(newdict)
#             elif newdict['RACE'] == 'Councilmember, Place No 3, District No 3 – City of Plano':
#                 print(newdict)
                
#             datalist.append(newdict)
        
#         except Exception as e:
#             # print(item)
#             print(combined_row)
#             print(e)
    
#     prev_row = row
    
# # save it, and the next step is for clarity to ingest this
# ndf = pd.DataFrame(datalist)
# ndf.to_csv(fname+'_parsed.csv', index=False)

# results = {}

# groups = ndf.groupby(['RACE', 'CANDIDATE', 'UNEDITED'])

# for name, group in groups:
#     race, candidate, unedited = name
    
#     # print(race)
    
#     # Custom workaround to catch Proposition A/B for Town of Prosper, and Councilmember at Large for City of Parker
#     if race == 'Proposition A':
#         race = unedited.split('.')[0]
#         if 'For' in race:
#             race = 'Proposition A - Town of Prosper'
#     elif race == 'Proposition B':
#         race = unedited.split('.')[0].replace('  ', ' ')
#         if 'For' in race:
#             race = 'Proposition B - Town of Prosper'
#     elif race == 'Councilmember At':
#         race = unedited.split('.')[0]
#         if 'Cindy Meyer' in race :
#             race = 'Councilmember At-Large – City of Parker'
#     elif race == 'Council Member, At':
#         race = unedited.split('City of McKinney')[0]+'City of McKinney'
    
#     if race not in results:
#         results[race] = {
#             "ballots cast": "0",
#             "precincts reporting": "0",
#             "precincts total": "0",
#             "registered voters": "0",
#             "choices": {},
#             # "unedited": race['UNEDITED']
#         }
    
#     # if race == 'Councilmember, Place No 1, District No 1 – City of Plano':
#     #     print(race)
#     #     print(group)
    
#     for _, row in group.iterrows():
#         candidate = row["CANDIDATE"]
#         if candidate not in ["OVER VOTES", "UNDER VOTES"]:
#             total_votes = row["VOTES"]
#             # vote_pct = "{:.2f}".format(int(total_votes) / float(group["VOTES"].sum()))
#             if candidate not in results[race]["choices"]:
#                 results[race]["choices"][candidate] = {
#                     "total_votes": int(total_votes),
#                     "vote_pct": "0.00"
#                 }
#             else:
#                 results[race]["choices"][candidate]["total_votes"] += int(total_votes)
#                 results[race]["choices"][candidate]["vote_pct"] = "0.00"

# for race, race_data in results.items():
#     # print(race)
#     if race == 'Councilmember, Place No 1, District No 1 – City of Plano':
#         print(race_data['choices'])
#     choices = race_data['choices']
#     total_votes = sum(c_data['total_votes'] for c_data in choices.values())
#     for choice_data in choices.values():
#         choice_data['vote_pct'] = '{:.2f}'.format(choice_data['total_votes'] / total_votes) if total_votes > 0 else '0.00'


# result_string = json.dumps(results)

# with open("data/"+ftime+".json", "w") as json_file:
#     json_file.write(result_string)
    
# with open("data/latest.json", "w") as json_file:
#     json_file.write(result_string)
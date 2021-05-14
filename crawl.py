import requests
import re
import html
import pandas as pd
import pickle 
import time

account = input('Input your account name. (Aime): ')
password = input('Input your password: ')
print('Enter Login Page...')
login_1 = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/'
response = requests.get(login_1)
cookies = response.headers['Set-Cookie']

print('Try to login...')
login_page = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login/sid/'
response = requests.post(login_page, headers={'cookie': cookies}, data={'retention':1,'sid': account,'password':password}, allow_redirects=False)
redirect_page = response.headers['location']
print('redirect to:', response.headers['location'])
cookies = response.cookies

response = requests.get(redirect_page, cookies=cookies, allow_redirects=False)
cookies = response.cookies
if '_t' not in cookies:
    print("Account or Password is invalid. Quit the program.")
    exit()

print('Get userId successfully.')

def parse(data):
    data = re.sub(r'(\n|\r|\t)', ' ', data)
    result = []
    for lev in ['basic', 'advanced', 'expert', 'master']:
      music_box = re.findall(f'<div class="w388 musiclist_box bg_{lev}">.*?</form>', data)
      for single_list in music_box:
          title = re.findall(r'div class="music_title">.*?</div>', single_list)[0]
          title = re.findall(r'>.*?<', html.unescape(title))[0][1:-1]
          score = re.findall(r'<span class="text_b">.*?</span>', single_list)
          if len(score) == 0:
              score = 0
          else:
            score = re.findall(r'>.*?<', score[0])[0][1:-1]
            score = score.replace(',', '')
          result.append([lev, title, score])
    return result


extract_datas = []

def job_request(lev):
  global extract_datas
  # process the showing levels
  output_lev = None
  if lev <= 6:
    output_lev = str(lev + 1)
  else:
    output_lev = str(7 + (lev - 6) // 2) 
    if lev % 2 == 1:
      output_lev += '+'

  requests.post('https://chunithm-net-eng.com/mobile/record/musicLevel/sendSearch/', cookies=cookies, data={'level':lev, 'token':cookies["_t"]})
  response = requests.get('https://chunithm-net-eng.com/mobile/record/musicLevel/search', cookies=cookies)
  data = response.content

  result = parse(data.decode())
  print('Get the scores of level', output_lev, f'successfully (num:{len(result)}).')
  extract_datas += [(output_lev, *row) for row in result if int(row[-1]) != 0]

for lev in range(21):
    job_request(lev)

split_datas = list(map(list, zip(*extract_datas)))
dict_for_df = { k:v for k, v in zip(['level', 'music_level', 'title', 'score'], split_datas)}
df = pd.DataFrame(data=dict_for_df)
print("Output to csv. (named as output.csv)")
df.to_csv('output.csv', index=False, encoding='utf-8-sig')

print("Now, try to analyze your rating in each song.")
time.sleep(1)

def score_to_rating(score, hidden_lev):
    # rating transformer
    if score > 1007500:
        return hidden_lev + 2
    elif score > 1005000:
        return hidden_lev + 1.5 + (score - 1005000) / (1007500 - 1005000) * 0.5
    elif score > 1000000:
        return hidden_lev + 1 + (score - 1000000) / (1005000 - 1000000) * 0.5
    elif score > 975000:
        return hidden_lev + 0 + (score - 975000) / (1000000 - 975000) * 1
    elif score > 925000:
        return hidden_lev + -3 + (score - 925000) / (975000 - 925000) * 3
    elif score > 900000:
        return hidden_lev + -5 + (score - 900000) / (925000 - 900000) * 2
    elif score > 800000:
        return (hidden_lev - 5) / 2 + (score - 800000) / (900000 - 800000) * ((hidden_lev + -5) - (hidden_lev - 5) / 2)
    elif score > 500000:
        return 0 + (score - 500000) / (800000 - 500000) * (hidden_lev - 5) / 2
    else:
        return 0

info = pickle.load(open('hidden_lev.pkl', 'rb'))
df = pd.read_csv('output.csv')
hidden_levs = []
rating = []
to_top = []
for row in df.iterrows():
    title = row[1]['title'].strip()
    score = int(row[1]['score'])
    music_level = row[1]['music_level']
    if music_level == 'expert':
        music_level = 'EXP'
    elif music_level == 'master':
        music_level = 'MAS'
    target_n = '?'
    if title in info:
        for song_lev, song_hidden_lev in info[title]:
            if music_level == song_lev:
                target_n = song_hidden_lev
    if target_n != '?':
        rating.append(score_to_rating(score,  float(target_n)))
        to_top.append(2 - score_to_rating(score,  float(target_n)) + float(target_n))
        
    else:
        rating.append(-1)
        to_top.append(-1)
    hidden_levs.append(target_n)
    # print(title, target_n)

df.insert(4, 'hidden', hidden_levs)
df.insert(5, 'rating', rating)
df.insert(6, 'to_top', to_top)
df = df.sort_values(by=['rating'], ascending=False)
print("Output to csv. (named as analysis.csv)")
df.to_csv('analysis.csv', index=False, encoding='utf-8-sig')
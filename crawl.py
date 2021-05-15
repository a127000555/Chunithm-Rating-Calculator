from numpy.lib.type_check import imag
import requests
import re
import html
import pandas as pd
import pickle
import time
import pickle
import os
import json
from getpass import getpass
account = input('Input your account name. (Aime): ')
password = getpass('Input your password: ')

print('Enter Login Page...')
login_1 = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login?site_id=chuniex&redirect_url=https://chunithm-net-eng.com/mobile/&back_url=https://chunithm.sega.com/'
response = requests.get(login_1)
cookies = response.headers['Set-Cookie']

print('Try to login...')
login_page = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login/sid/'
response = requests.post(login_page, headers={'cookie': cookies}, data={
                         'retention': 1, 'sid': account, 'password': password}, allow_redirects=False)
redirect_page = response.headers['location']
print('redirect to:', response.headers['location'])
cookies = response.cookies

response = requests.get(redirect_page, cookies=cookies, allow_redirects=False)
cookies = response.cookies
if '_t' not in cookies:
  print("Account or Password is invalid. Quit the program.")
  exit()

print('Get userId successfully.')

# Try to load idx2img data
try:
  idx2img_url = pickle.load(open('idx2img.pkl', 'rb'))
except Exception as e:
  print("igx2img.pkl not found, will generate new one.")
  idx2img_url = {}

def parse(data):
  data = re.sub(r'(\n|\r|\t)', ' ', data)
  result = []
  for lev in ['basic', 'advanced', 'expert', 'master']:
    music_box = re.findall(
      f'<div class="w388 musiclist_box bg_{lev}">.*?</form>', data)
    for single_list in music_box:
      title = re.findall(r'div class="music_title">.*?</div>', single_list)[0]
      title = re.findall(r'>.*?<', html.unescape(title))[0][1:-1]
      score = re.findall(r'<span class="text_b">.*?</span>', single_list)
      music_idx = re.findall(r'<input type="hidden" name="idx" value=".*?" />', single_list)[0][39:-4]
      if len(score) == 0:
        score = 0
      else:
        score = re.findall(r'>.*?<', score[0])[0][1:-1]
        score = score.replace(',', '')

      if int(music_idx) not in idx2img_url:
        requests.post('https://chunithm-net-eng.com/mobile/record/musicGenre/sendMusicDetail/',
          cookies=cookies, data={'idx': music_idx, 'token': cookies["_t"]})
        response = requests.get(
          'https://chunithm-net-eng.com/mobile/record/musicDetail/', cookies=cookies)
        tmp = re.findall(r'play_jacket_img.*?</div>', response.content.decode(), flags=re.DOTALL)
        img_url = re.findall(r'https://.*?.jpg', tmp[0])[0]
        idx2img_url[int(music_idx)] = img_url
        print(f"[Update] Get music ({title}) image url: {img_url}")
      else:
        img_url = idx2img_url[int(music_idx)]
      result.append([lev, title, score, img_url])
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

    requests.post('https://chunithm-net-eng.com/mobile/record/musicLevel/sendSearch/',
                  cookies=cookies, data={'level': lev, 'token': cookies["_t"]})
    response = requests.get(
        'https://chunithm-net-eng.com/mobile/record/musicLevel/search', cookies=cookies)
    data = response.content

    result = parse(data.decode())
    print('Get the scores of level', output_lev,
          f'successfully (num:{len(result)}).')
    extract_datas += [(output_lev, *row)
                      for row in result if int(row[-2]) != 0]


for lev in range(21):
    job_request(lev)

split_datas = list(map(list, zip(*extract_datas)))
dict_for_df = {k: v for k, v in zip(
    ['level', 'music_level', 'title', 'score', 'img_url'], split_datas)}
df = pd.DataFrame(data=dict_for_df)
outDf = df
outDf = outDf.filter(regex="^(?!(img_url)$).*$")
print("Output to csv. (named as output.csv)")
df.to_csv('tmp.csv', index=False, encoding='utf-8-sig')
outDf.to_csv('output.csv', index=False, encoding='utf-8-sig')

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


info = json.load(open('hidden_lev.json', 'rb'))
df = pd.read_csv('tmp.csv')
os.remove("tmp.csv")
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
        to_top.append(2 - score_to_rating(score,
                      float(target_n)) + float(target_n))

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

anaDf = df
anaDf.filter(regex="^(?!(img_url)$).*$")
anaDf.to_csv('analysis.csv', index=False, encoding='utf-8-sig')

# update idx2img
print("Update idx2img.pkl...")
pickle.dump(idx2img_url, open('idx2img.pkl', 'wb'))

  
# style="background-image: linear-gradient(to top, blue, green, yellow, orange, red); text-shadow: 0 0 1px #000;  -webkit-background-clip: text;
#   color: transparent;"
def generate_color(rating):
  if rating == '?':
    return '?'
  r = float(rating)
  color = ""
  if r >= 15:
    color = "linear-gradient(to top, blue, green, yellow, orange, red)"
  elif r >= 14.5:
    color = 'linear-gradient(to top, gold,yellow,gold);'
  elif r >= 14:
    color = 'linear-gradient(to top, orange,yellow,gold,orange);'
  elif r >= 13:
    color = 'linear-gradient(to top, gray,silver,gray);'
  elif r >= 12:
    color = 'linear-gradient(to top, brown,orange,brown);'
  elif r >= 10:
    color = 'violet'
  elif r >= 7:
    color = 'red'
  elif r >= 4:
    color = 'orange'
  else:
    color = 'green'


  return f'''
    <span style="
      background-image: {color}; 
      -webkit-text-stroke: 0.5px black;
      font-weight:1000;
      -webkit-background-clip: text;
      color: transparent;"> {r} </span>
      '''
def generate_rank_icon(score):
  score = int(score)
  img_idx = 0
  if score >= 1_007_500:
    img_idx = 10
  elif score >= 1_000_000:
    img_idx = 9
  elif score >= 975_000:
    img_idx = 8
  elif score >= 950_000:
    img_idx = 7
  elif score >= 925_000:
    img_idx = 6
  elif score >= 900_000:
    img_idx = 5
  elif score >= 800_000:
    img_idx = 4
  elif score >= 700_000:
    img_idx = 3
  elif score >= 600_000:
    img_idx = 2
  elif score >= 500_000:
    img_idx = 1
  else:
    img_idx = 0
  return f'''
    <img src="https://chunithm-net-eng.com/mobile/images/icon_rank_{img_idx}.png" style="width:35px; 
      text-align: right;">
  ''' 

def generate_block(idx, level, music_level, title, score, hidden, rating, to_top, img_url):
  hidden2 = '?'
  if hidden != '?':
    if len(hidden.split('.')) == 1:
      hidden2 = int(hidden) + 2
    else:
      i, f = hidden.split('.')
      hidden2 = str(int(i)+2) + '.' + f
    rating = '%.3f' % rating
    rating = float(rating)
    to_top = '%.3f' % (float(hidden2) - rating)
  else:
    rating = '?'
    to_top = '?'
  return f'''
  <div class="w388 musiclist_box bg_{music_level}" style="display:flex;">
      <div class="play_jacket_area" style="background-color: #FFFFFF80; display:inline-block;">
          <div class="play_jacket_img" >
              <img src="{img_url}" />
          </div>
      </div>
      <div style="inline-block; clear: both; width:100%">
          <div class="music_title" style="font-size: 11px; text-align:center;">
              <span>
                  #{idx} {title}
              </span>
          </div>
          <div>
              <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;" >
                  <span> SCORE：<span class="text_b">{score} {generate_rank_icon(score)} </span> 
              </div>
              <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;">
                  <span> LEVEL：<span class="text_b">{level} / {hidden}</span>
              </div>
              <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;">
                  <span> RATING：<span class="text_b">{generate_color(rating)} <!-- {hidden2}--> (-{to_top})</span>
              </div>
          </div>
      </div>
  </div>
  '''

# Get User Data
response = requests.get(
    'https://chunithm-net-eng.com/mobile/home/', cookies=cookies)
response_content = response.content.decode()
filtered_pattern = [
    r'<div id="main_menu">.*?</div>',
    r'<div class="box05 w420 text_l">' + r'.*?</div>'*2,
    r'<div class="box05 w420">' + r'.*?</div>'*3,
    r'<div class="sitemap">' + r'.*?</div>'*3,
    r'<div id="footer">' + r'.*?</div>'*4,
]
for pattern in filtered_pattern:
    response_content = re.sub(pattern, "", response_content, flags=re.DOTALL)
clean_template = response_content



# Generate Rating Color in User information
p = re.compile(r'<div class="player_rating">.*?</div>', flags=re.DOTALL)
searchL, searchR = p.search(clean_template).span()
findRatingRaw = clean_template[searchL:searchR]
A = re.findall(r':.*?/', findRatingRaw)[0].strip()
B = re.findall(r'</span>.*?\)', findRatingRaw)[0].strip()
rating = A[1:-1]
clean_template = clean_template[:searchL] + f'''
  <div class="player_rating">
    RATING : {generate_color(rating)} / 
    (<span class="font_small">MAX</span> {generate_color(B[8:-1])})
  </div>
  ''' + clean_template[searchR+1:]

# Generate score blocks
firstblocks = []
secondblocks = []
best30_sum = 0
best10_sum = 0
for i, row in enumerate(df.iterrows()):
  if i < 10:
    best10_sum+=row[1]['rating']
  if i < 30:
    best30_sum+=row[1]['rating']
  if i <= 29:
    firstblocks.append(generate_block(i+1, **row[1]))
  else:
    secondblocks.append(generate_block(i+1, **row[1]))


replaced = f'''
  <div class="mt_15">
    <h2 id="page_title">
      ANALYSIS
    </h2>
  </div>
  <div class="w420 box_player clearfix">
    <div>
      <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;" >
          <span> BEST30：<span class="text_b">{generate_color("%.3f" % (best30_sum / 30))} </span> 
      </div>
      <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;">
          <span> RECENT10：<span class="text_b"> {generate_color("%.3f" % (float(rating) * 2 - best30_sum / 30))} </span>
      </div>
      <div class="play_musicdata_highscore" style="width:90% !important; font-size: 12px;">
          <span> MAX RATING：<span class="text_b">{generate_color("%.3f" % ((best30_sum/30 + best10_sum/10)/2))}</span>
      </div>
    </div>
  </div>
  <hr class="line_dot_black w420">

  <div class="mt_15">
    <h2 id="page_title">
      BEST30
    </h2>
  </div>
  <hr class="line_dot_black w420">
  <div class="mt_10">
    {''.join(firstblocks)}
  </div>
  <div class="mt_15">
    <h2 id="page_title">
      BEST30~
    </h2>
  </div>
  <hr class="line_dot_black w420">
  <div class="mt_10">
    {''.join(secondblocks)}
  </div>
'''


p = re.compile(r'class="frame01_inside w450"' +
               r'.*?</div>'*13, flags=re.DOTALL)



inner_start, inner_end = p.search(clean_template).span()
output = clean_template[:inner_end] + replaced + clean_template[inner_end:]
# print(clean_template[inner_start:inner_end])
# print(output)

# clean_template = re.sub(r'<div class="sleep', clean_template, replaced, flags=re.DOTALL)
with open("visualize.html", 'wb') as fout:
    fout.write(output.encode())


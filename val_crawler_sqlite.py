import requests, os
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
import unicodedata

# 官網爬取VCT隊伍名單
def get_region():
    url = 'https://valorantesports.com/zh-TW/season/113481389624036511/handbook'
    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    
    VCT = bs.find_all(class_=
    'bd_1px_solid_{colors.stroke.border.primary} bdr_xs c_unifiedText.secondary d_flex flex-d_column gap_8 px_16 py_24 textStyle_label/lg'
    )
    
    global regions_list
    regions_list = []
    for num, regions in enumerate(VCT):
        region = regions.find(class_='ai_center d_flex flex-d_column gap_8 py_8')
        regions_list.append([region.text])
        for teams in regions.find_all(class_=
    'ai_center d_flex flex_0_1_auto flex-d_column gap_8 jc_flex-end py_16 textStyle_label/lg'
    ):
            regions_list[num].append(teams.text)   
    # 確認隊伍資訊        
    for _ in regions_list:
        print(_)

# 正規化隊伍名稱
def normalization(teams_name):
    return ''.join(
        # 將字串正規化成'分解'形式
        letter for letter in unicodedata.normalize('NFD', teams_name)
        # 過濾掉Nonspacing Mark
        if unicodedata.category(letter) != 'Mn')

# 增加賽區欄位        
def add_region(team):
    if team in amer:
        return 'AMER'
    elif team in emea:
        return 'EMEA'
    elif team in apac:
        return 'APAC'
    elif team in cn:
        return 'CN'
    else:
        print("'%s' not in the area" % team)
        return 'Other'

# 處理CL欄位    
def cl_to_float(row):
    if row['CL'] == '':
        return np.nan
    elif row['CL%'] == '':
        return 0.0
    else:
        return float(row['CL%'].rstrip('%')) / 100
    
# 百分比轉浮點數
def percent_to_float(df, column):
    df[column] = df[column].str.rstrip('%').astype(float) / 100
    
    
# 爬蟲抓取資料
# 主網址
url = 'https://www.vlr.gg'

# stats
event_group_id = 74   #champions_tour2025
region = 'all'
min_rounds = 100
min_rating = 1550
agent = 'all'
map_id = 'all'
timespan = '60d'
url_stats = f'https://www.vlr.gg/stats/?event_group_id={event_group_id}&region={region}&min_rounds={min_rounds}&min_rating={min_rating}&agent={agent}&map_id={map_id}&timespan={timespan}'

res = requests.get(url_stats)
bs = BeautifulSoup(res.text, 'lxml')

# 抓表頭
thead = bs.find_all('th')
thead_list = []

for i in thead:
    thead_list.append(i.text)

# 表格內容
tbody = bs.find('tbody')
# 抓每列資料
players = tbody.find_all('tr')
players_list = []
agent_list = []     # agent為圖片，另外處理
player_url = [] # 選手頁面的網址

for player_index, player in enumerate(players):
    # 每列一個list
    players_list.append([])
    agent_list.append([])
    pic_href = url + player.find('a').get('href')
    player_url.append(pic_href)
    # 每一格資料
    player_stats = player.find_all('td')
    # 每列資料存成一個list
    for stat in player_stats:
        players_list[player_index].append(stat.text.strip())
        # agent欄位為圖片，抓取圖片檔中的文字
        agents = stat.find_all('img')
        # 每列一個list
        for agent in agents:
            agent_list[player_index].append(agent.get('src').split('/')[-1][0:-4])


# 抓個人資料
picture_url = []
picture_name = []
detail_stats = []
thead_personal = False

for index, pic in enumerate(player_url):
    res = requests.get(pic)
    bs = BeautifulSoup(res.text, 'lxml')
    # 到每個選手頁面抓照片
    try:
        picture = bs.find('img', {'src':re.compile('^//owcdn')})
        name =  f'{index}_' + picture.get('alt') + '.png'
        src = 'https:' + picture.get('src')
    # 無照片時的處理
    except:
        name = f'{index}_' + bs.find('h1').text.strip() + '.png'
        src = 'https://www.vlr.gg/img/base/ph/sil.png'
    picture_url.append(src)
    picture_name.append(name)
    
    # 抓個人數據欄名
    if not thead_personal:
        thead_personal = bs.find('thead').text.split()
        
    # 抓個人詳細數據
    tbody = bs.find('tbody')
    for tr in tbody.find_all('tr'):
        detail_stats.append([index] + [tr.find('img').get('alt')] + tr.text.split())
    
    
# 在工作目錄下建立目錄pics來儲存圖片
folder = 'pics'
if not os.path.exists(folder):
    os.mkdir(folder)
# 下載圖片到目錄
picture_list = []
for pic, name in zip(picture_url, picture_name):
    try:
        img = requests.get(pic)
        path = os.path.join(folder, name)
        with open(path, 'wb') as f:
            f.write(img.content)
        picture_list.append(path)
    #無法下載的圖檔
    except: 
        print('無法下載:%s' % name)


# 資料處理
# 抓取的資料儲存成一個DataFrame
stats = pd.DataFrame(players_list, columns=thead_list)
# 檢查資料
print(stats.info())
get_region()

# 隊伍分區
# amer = ['G2', '100T', 'SEN', 'C9', 'NRG', 'EG', 'MIBR', 'KRÜ', '2G', 'LOUD', 'LEV', 'FUR']
# emea = ['TH', 'FNC', 'NAVI', 'VIT', 'TL', 'BBL', 'FUT', 'KC', 'GX', 'APK', 'MKOI', 'M8']
# apac = ['BME', 'DRX', 'GEN', 'PRX', 'RRQ', 'TLN', 'T1', 'NS', 'GE', 'DFM', 'ZETA', 'TS']
# cn = ['EDG', 'TEC', 'NOVA', 'DRG', 'BLG', 'XLG', 'WOL', 'TE', 'FPX', 'TYL', 'JDG', 'AG']
apac = regions_list[0]
amer = regions_list[1]
cn = regions_list[2]
emea = regions_list[3]


# 將選手跟隊名分隔出來
player_name = []
player_team = []
for player in stats['Player']:
    player_name.append(player.split()[0])
    player_team.append(player.split()[1])
# 更新成選手欄位和隊伍欄位    
stats['Player'] = player_name
stats.insert(1, column='Team', value=player_team)

# 修改隊伍標籤
stats['Team'] = stats['Team'].apply(normalization)
stats.loc[stats['Player'] == 'whzy', 'Team'] = 'BLG'
stats.loc[stats['Player'] == 'cortezia', 'Team'] = 'MIBR'
stats.loc[stats['Player'] == 'xeus', 'Team'] = 'FUT'

# 新增地區欄位
stats_region = stats['Team'].apply(add_region)
stats.insert(2, column='Region', value=stats_region)

# 選手照片 
stats['Picture'] = picture_list

# Agents_list 轉成字串
stats['Agents'] = agent_list
stats['Agents'] = stats['Agents'].apply(lambda x: ','.join(x))

# 百分比字串 > 浮點數
percent_to_float(stats, 'KAST')
percent_to_float(stats, 'HS%')

# 先處理空值再轉成浮點數
stats['CL%'] = stats.apply(cl_to_float, axis=1)
stats['CL'] = np.where(stats['CL'] == '', '0/0', stats['CL'])

# 修改欄位名稱
stats = stats.rename(columns={'R2.0':'Rating', 'K:D':'KD', 'HS%':'HS', 'CL%':'CL', 'CL':'CL_Total'})

# 其餘字串型態轉為float或int
str_to_digit = {
    'Rnd': int,
    'Rating': float,
    'ACS': float,
    'KD': float,
    'ADR': float,
    'KPR': float,
    'APR': float,
    'FKPR': float,
    'FDPR': float,
    'KMax': int,
    'K': int,
    'D': int,
    'A': int,
    'FK': int,
    'FD': int
}

stats = stats.astype(str_to_digit)
print(stats.info())



# 個人資料處理
thead_personal = ['PlayerID','Agent','Count'] + thead_personal
personal_stats = pd.DataFrame(detail_stats, columns=thead_personal)

# 處理遺漏值
personal_stats['Rating2.0'] = personal_stats['Rating2.0'].astype(float)
mask = (personal_stats.iloc[:,5] > 10) | (personal_stats.iloc[:,-1].isna())
personal_stats.loc[mask, personal_stats.columns[5:]] = np.nan

# 刪除多餘欄位
personal_stats.drop('Use',axis=1,inplace=True)

# 取數值
personal_stats['Count'] = personal_stats['Count'].str.strip('()').astype(int)

# 百分比字串 > 浮點數
percent_to_float(personal_stats, 'KAST')

# ID改為name方便查詢
personal_player = personal_stats['PlayerID'].map(stats['Player'])
personal_stats['PlayerID'] = personal_player

# 修改欄位名稱
personal_stats = personal_stats.rename(columns={'PlayerID':'Player', 'Rating2.0':'Rating', 'K:D':'KD'})

# 修改欄位型態
str_to_digit = {
    'RND': int,
    'ACS': float,
    'KD': float,
    'ADR': float,
    'KPR': float,
    'APR': float,
    'FKPR': float,
    'FDPR': float,
    'K': float,
    'D': float,
    'A': float,
    'FK': float,
    'FD': float
}
personal_stats = personal_stats.astype(str_to_digit)


# 建立資料庫連線
engine = create_engine("sqlite:///vlrgg.db")
# 寫入stats資料表
stats.to_sql(name='valorant_stats', con=engine, if_exists='replace', index=False)
# 寫入personal_stats資料表
personal_stats.to_sql(name='personal_stats', con=engine, if_exists='replace', index=False)

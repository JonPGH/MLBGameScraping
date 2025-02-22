from datetime import datetime, timezone
import time 
import pytz, streamlit as st, requests, pandas as pd, os, numpy as np

st.set_page_config(
    page_title="JonPGH MLB Game Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Functions
def dropUnnamed(df):
  df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
  return(df)

def getLiveGames(date_string):
    games = []
    #sportIds = [1,11, 12, 13, 14, 15, 16, 17]
    sportIds = [1]
    sport_id_mappings = {1: 'MLB', 11: 'AAA', 12: 'AA', 13: 'A+', 14: 'A', 16: 'ROK', 17: 'WIN'}

    for sportId in sportIds:
        url = "https://statsapi.mlb.com/api/v1/schedule/?sportId={}&date={}".format(sportId,date_string)
        schedule = requests.get(url).json()

        for date in schedule["dates"]:
            for game_data in date["games"]:
                # Skip games that are not finished ("F")
                # If a game was delayed, it will show up again on a later calendar date
                #if game_data["status"]["codedGameState"] == "F":
                game = {}
                game["date"] = date_string
                game["game_id"] = game_data["gamePk"]
                game["game_type"] = game_data["gameType"]
                game["venue_id"] = game_data["venue"]["id"]
                game["venue_name"] = game_data["venue"]["name"]
                game["away_team"] = game_data["teams"]["away"]["team"]["name"]
                game["home_team"] = game_data["teams"]["home"]["team"]["name"]
                game["league_id"] = sportId
                game["league_level"] = sport_id_mappings.get(sportId)
                game["game_status"] = game_data["status"]["codedGameState"]
                game["game_status_full"] = game_data["status"]["abstractGameState"]
                game["game_start_time"] = game_data["gameDate"]
                games.append(game)
    return games

def get_MILB_PBP_Live(game_info_dict):
  game_pk = game_info_dict.get('game_id')
  game_date = game_info_dict.get('date')
  venue_id = game_info_dict.get('venue_id')
  venue_name = game_info_dict.get('venue_name')
  league_id = game_info_dict.get('league_id')
  game_type = game_info_dict.get('game_type')

  # get game play by play
  url = 'https://statsapi.mlb.com/api/v1/game/{}/playByPlay'.format(game_pk)

  boxurl = 'https://statsapi.mlb.com/api/v1/game/{}/boxscore'.format(game_pk)
  box_game_info = requests.get(boxurl).json()
  lgname=box_game_info.get('teams').get('away').get('team').get('league').get('name')
  away_team = box_game_info.get('teams').get('away').get('team').get('name')
  away_team_id =  box_game_info.get('teams').get('away').get('team').get('id')
  home_team = box_game_info.get('teams').get('home').get('team').get('name')
  home_team_id = box_game_info.get('teams').get('home').get('team').get('id')

  game_info = requests.get(url).json()
  jsonstr = str(game_info)

  savtest='startSpeed' in jsonstr
  if savtest is True:
    statcastflag='Y'
  else:
    statcastflag='N'

  allplays = game_info.get('allPlays')

  gamepbp = pd.DataFrame()
  for play in allplays:
    currplay = play
    inningtopbot = currplay.get('about').get('halfInning')
    inning = currplay.get('about').get('inning')
    actionindex = currplay.get('actionIndex')
    at_bat_number = currplay.get('about').get('atBatIndex')+1
    currplay_type = currplay.get('result').get('type')
    currplay_res = currplay.get('result').get('eventType')
    currplay_descrip = currplay.get('result').get('description')
    currplay_rbi = currplay.get('result').get('rbi')
    currplay_awayscore = currplay.get('result').get('awayscore')
    currplay_homescore = currplay.get('result').get('homescore')
    currplay_isout = currplay.get('result').get('isOut')
    playdata = currplay.get('playEvents')
    playmatchup = currplay.get('matchup')
    bid = playmatchup.get('batter').get('id')
    bname = playmatchup.get('batter').get('fullName')
    bstand = playmatchup.get('batSide').get('code')
    pid = playmatchup.get('pitcher').get('id')
    pname = playmatchup.get('pitcher').get('fullName')
    pthrows = playmatchup.get('pitchHand').get('code')

    for pitch in playdata:
      pdetails = pitch.get('details')
      checkadvise = pdetails.get('event')
      pitch_number = pitch.get('pitchNumber')
      if checkadvise is None:
        try:
          description = pdetails.get('call').get('description')
        except:
          description=None
        inplay = pdetails.get('isInPlay')
        isstrike = pdetails.get('isStrike')
        isball = pdetails.get('isBall')
        try:
          pitchname = pdetails.get('type').get('description')
          pitchtype = pdetails.get('type').get('code')
        except:
          pitchname=None
          pitchtype=None

        ballcount = pitch.get('count').get('balls')
        strikecount = pitch.get('count').get('strikes')
        try:
          plate_x = pitch.get('pitchData').get('coordinates').get('x')
          plate_y = pitch.get('pitchData').get('coordinates').get('y')
        except:
          plate_x = None
          plate_y = None

        try:
          startspeed = pitch.get('pitchData').get('startSpeed')
          endspeed = pitch.get('pitchData').get('endspeed')
        except:
          startspeed=None
          endspeed=None

        try:
          kzonetop = pitch.get('pitchData').get('strikeZoneTop')
          kzonebot = pitch.get('pitchData').get('strikeZoneBottom')
          kzonewidth = pitch.get('pitchData').get('strikeZoneWidth')
          kzonedepth = pitch.get('pitchData').get('strikeZoneDepth')
        except:
          kzonetop=None
          kzonebot=None
          kzonewidth=None
          kzonedepth=None


        try:
          ay = pitch.get('pitchData').get('coordinates').get('aY')
          ax = pitch.get('pitchData').get('coordinates').get('aX')
          pfxx = pitch.get('pitchData').get('coordinates').get('pfxX')
          pfxz = pitch.get('pitchData').get('coordinates').get('pfxZ')
          px = pitch.get('pitchData').get('coordinates').get('pX')
          pz = pitch.get('pitchData').get('coordinates').get('pZ')
          breakangle = pitch.get('pitchData').get('breaks').get('breakAngle')
          breaklength = pitch.get('pitchData').get('breaks').get('breakLength')
          break_y= pitch.get('pitchData').get('breaks').get('breakY')
          zone = pitch.get('pitchData').get('zone')
        except:
          ay=None
          ax=None
          pfxx=None
          pfxz=None
          px=None
          pz=None
          breakangle=None
          break_y=None
          breaklength=None
          zone=None

        try:
          hitdata = pitch.get('hitData')
          launchspeed = pitch.get('hitData').get('launchSpeed')
          launchspeed_round = round(launchspeed,0)
          launchangle = pitch.get('hitData').get('launchAngle')
          launchangle_round = round(launchangle,0)
          bb_type = pitch.get('hitData').get('trajectory')
          hardness = pitch.get('hitData').get('hardness')
          location = pitch.get('hitData').get('location')
          total_distance = pitch.get('hitData').get('totalDistance')
          coord_x = pitch.get('hitData').get('coordinates').get('coordX')
          coord_y = pitch.get('hitData').get('coordinates').get('coordY')

        except:
          #print('No hit data')
          launchspeed = None
          launchangle = None
          get_lsa = None
          bb_type = None
          hardness = None
          location = None
          coord_x = None
          coord_y = None


        this_gamepbp = pd.DataFrame({'StatcastGame': statcastflag,
                                  'game_pk': game_pk, 'game_date': game_date, 'game_type': game_type, 'venue': venue_name,
                                  'venue_id': venue_id,'league_id': league_id, 'league': lgname, 'level': levdict.get(lgname),
                                  'away_team': away_team,'away_team_id': away_team_id, 'away_team_aff': affdict.get(away_team),
                                  'home_team': home_team, 'home_team_id': home_team_id, 'home_team_aff': affdict.get(home_team),
                                  'player_name': pname, 'pitcher': pid, 'BatterName': bname, 'batter': bid,
                                  'stand': bstand, 'p_throws': pthrows,'inning_top_bot': inningtopbot,
                                  'plate_x': plate_x, 'plate_y': plate_y,
                                  'inning': inning, 'at_bat_number':at_bat_number, 'pitch_number': pitch_number,
                                  'description': description, 'play_type': currplay_type, 'play_res':currplay_res,
                                  'play_desc': currplay_descrip,
                                  'rbi': currplay_rbi,'away_team_score':currplay_awayscore,
                                  'isOut': currplay_isout,'home_team_score':currplay_homescore,
                                  'isInPlay': inplay,'IsStrike':isstrike,'IsBall':isball,'pitch_name':pitchname,
                                  'pitch_type':pitchtype,'balls': ballcount,'strikes':strikecount,
                                  'release_speed':startspeed, 'end_pitch_speed': endspeed,'zone_top':kzonetop,
                                  'zone_bot':kzonebot,'zone_width':kzonewidth,'zone_depth':kzonedepth,'ay':ay,
                                  'ax':ax,'pfx_x':pfxx,'pfx_z':pfxz,'px':px,'pz':pz,'break_angle':breakangle,
                                  'break_length':breaklength,'break_y':break_y,'zone':zone,
                                  'launch_speed': launchspeed, 'launch_angle': launchangle,# 'hit_distance': total_distance,
                                  'bb_type':bb_type,'hit_location': location,'hit_coord_x': coord_x,
                                  'hit_coord_y': coord_y},index=[0])
        gamepbp = pd.concat([gamepbp,this_gamepbp])


      else:
        #print('Found game advisory: {}'.format(checkadvise))
        pass
  gamepbp = gamepbp.reset_index(drop=True)
  #gamepbp.to_csv('/content/drive/My Drive/FLB/2024/LiveGames/AllPlayByPlay/{}_pbp.csv'.format(game_pk))
  return(gamepbp)

def savAddOns(savdata):
  pdf = savdata.copy()

  pdf['away_team_aff_id'] = pdf['away_team_id'].map(affdict)
  pdf['away_team_aff'] = pdf['away_team_aff_id'].map(affdict_abbrevs)
  pdf['home_team_aff_id'] = pdf['home_team_id'].map(affdict)
  pdf['home_team_aff'] = pdf['home_team_aff_id'].map(affdict_abbrevs)

  pdf['IsWalk'] = np.where(pdf['balls']==4,1,0)
  pdf['IsStrikeout'] = np.where(pdf['strikes']==3,1,0)
  pdf['BallInPlay'] = np.where(pdf['isInPlay']==1,1,0)
  pdf['IsHBP'] = np.where(pdf['description']=='Hit By Pitch',1,0)
  pdf['PA_flag'] = np.where((pdf['balls']==4)|(pdf['strikes']==3)|(pdf['BallInPlay']==1)|(pdf['IsHBP']==1),1,0)


  pdf['IsHomer'] = np.where((pdf['play_res']=='home_run')&(pdf['PA_flag']==1),1,0)

  pitchthrownlist = ['In play, out(s)', 'Swinging Strike', 'Ball', 'Foul',
        'In play, no out', 'Called Strike', 'Foul Tip', 'In play, run(s)','Hit By Pitch',
        'Ball In Dirt','Pitchout', 'Swinging Strike (Blocked)',
        'Foul Bunt', 'Missed Bunt', 'Foul Pitchout',
        'Intent Ball', 'Swinging Pitchout']

  pdf['PitchesThrown'] = np.where(pdf['description'].isin(pitchthrownlist),1,0)

  map_pitchnames = {'Two-Seam Fastball': 'Sinker', 'Slow Curve': 'Curveball', 'Knuckle Curve': 'Curveball'}
  pdf['pitch_name'] = pdf['pitch_name'].replace(map_pitchnames)

  swstrlist = ['Swinging Strike','Foul Tip','Swinging Strike (Blocked)', 'Missed Bunt']
  cslist = ['Called Strike']
  cswlist = ['Swinging Strike','Foul Tip','Swinging Strike (Blocked)', 'Missed Bunt','Called Strike']
  contlist = ['Foul','In play, no out', 'In play, out(s)', 'Foul Pitchout','In play, run(s)']
  swinglist = ['Swinging Strike','Foul','In play, no out', 'In play, out(s)', 'In play, run(s)', 'Swinging Strike (Blocked)', 'Foul Pitchout']
  klist = ['strikeout', 'strikeout_double_play']
  bblist = ['walk','intent_walk']
  hitlist = ['single','double','triple','home_run']
  #balllist = ['Ball','Automatic Ball','Intent Ball','Pitchout']
  palist = ['strikeout','walk']

  isstrikelist = [ 'Swinging Strike', 'Foul','Called Strike', 'Foul Tip','Swinging Strike (Blocked)',
                  'Automatic Strike - Batter Pitch Timer Violation', 'Foul Bunt',
                  'Automatic Strike - Batter Timeout Violation', 'Missed Bunt',
                  'Automatic Strike','Foul Pitchout','Swinging Pitchout']

  isballlist = ['Ball', 'Hit By Pitch','Automatic Ball - Pitcher Pitch Timer Violation',
                'Ball In Dirt','Pitchout', 'Automatic Ball - Intentional', 'Automatic Ball',
                'Automatic Ball - Defensive Shift Violation','Automatic Ball - Catcher Pitch Timer Violation',
                'Intent Ball']

  pdf['IsStrike'] = np.where(pdf['description'].isin(isstrikelist),1,0)
  pdf['IsBall'] = np.where(pdf['description'].isin(isballlist),1,0)


  pdf['BatterTeam'] = np.where(pdf['inning_top_bot']=='bottom', pdf['home_team'], pdf['away_team'])
  pdf['PitcherTeam'] = np.where(pdf['inning_top_bot']=='bottom', pdf['away_team'], pdf['home_team'])

  pdf['BatterTeam_aff'] = np.where(pdf['inning_top_bot']=='bottom', pdf['home_team_aff'], pdf['away_team_aff'])
  pdf['PitcherTeam_aff'] = np.where(pdf['inning_top_bot']=='bottom', pdf['away_team_aff'], pdf['home_team_aff'])

  pdf['IsBIP'] = pdf['BallInPlay']

  pdf['PA'] = pdf['PA_flag']
  #pdf['AB'] = np.where((pdf['IsBIP']+pdf['IsStrikeout'])>0,1,0)
  pdf['IsHit'] = np.where((pdf['PA']==1)&(pdf['play_res'].isin(hitlist)),1,0)

  pdf['IsSwStr'] = np.where(pdf['description'].isin(swstrlist),1,0)
  pdf['IsCalledStr'] = np.where(pdf['description'].isin(cslist),1,0)
  pdf['ContactMade'] = np.where(pdf['description'].isin(contlist),1,0)
  pdf['SwungOn'] = np.where(pdf['description'].isin(swinglist),1,0)
  pdf['IsGB'] = np.where(pdf['bb_type']=='ground_ball',1,0)
  pdf['IsFB'] = np.where(pdf['bb_type']=='fly_ball',1,0)
  pdf['IsLD'] = np.where(pdf['bb_type']=='line_drive',1,0)
  pdf['IsPU'] = np.where(pdf['bb_type']=='popup',1,0)

  pdf['InZone'] = np.where(pdf['zone']<10,1,0)
  pdf['OutZone'] = np.where(pdf['zone']>9,1,0)
  pdf['IsChase'] = np.where(((pdf['SwungOn']==1)&(pdf['InZone']==0)),1,0)
  pdf['IsZoneSwing'] = np.where(((pdf['SwungOn']==1)&(pdf['InZone']==1)),1,0)
  pdf['IsZoneContact'] = np.where(((pdf['ContactMade']==1)&(pdf['InZone']==1)),1,0)

  pdf['IsSingle'] = np.where((pdf['play_res']=='single')&(pdf['PA_flag']==1),1,0)
  pdf['IsDouble'] = np.where((pdf['play_res']=='double')&(pdf['PA_flag']==1),1,0)
  pdf['IsTriple'] = np.where((pdf['play_res']=='triple')&(pdf['PA_flag']==1),1,0)

  ablist = ['field_out', 'double', 'strikeout', 'single','grounded_into_double_play',
            'home_run','fielders_choice', 'force_out', 'double_play', 'triple','field_error',
            'fielders_choice_out','strikeout_double_play','other_out', 'sac_fly_double_play','triple_play']

  pdf['AB'] = np.where((pdf['play_res'].isin(ablist))&(pdf['PA_flag']==1),1,0)

  try:
    pdf = pdf.drop(['launch_speed_angle'],axis=1)
  except:
    pass

  pdf['launch_angle'] = pdf['launch_angle'].replace([None], np.nan)
  pdf['launch_speed'] = pdf['launch_speed'].replace([None], np.nan)

  pdf['launch_angle_round'] = round(pdf['launch_angle'],0)
  pdf['launch_speed_round'] = round(pdf['launch_speed'],0)

  pdf = pd.merge(pdf, lsaclass, how='left', on=['launch_speed_round','launch_angle_round'])

  pdf['launch_speed_angle'] = np.where(pdf['launch_speed_round']<60,1,pdf['launch_speed_angle'])
  pdf['launch_speed_angle'] = np.where((pdf['launch_speed_angle'].isna())&(pdf['launch_speed']>1),1,pdf['launch_speed_angle'])

  pdf['IsBrl'] = np.where(pdf['launch_speed_angle']==6,1,0)
  pdf['IsSolid'] = np.where(pdf['launch_speed_angle']==5,1,0)
  pdf['IsFlare'] = np.where(pdf['launch_speed_angle']==4,1,0)
  pdf['IsUnder'] = np.where(pdf['launch_speed_angle']==3,1,0)
  pdf['IsTopped'] = np.where(pdf['launch_speed_angle']==2,1,0)
  pdf['IsWeak'] = np.where(pdf['launch_speed_angle']==1,1,0)
  ###

  ## zone stuff
  pdf['IsCalledStr'] = np.where(pdf['description']=='Called Strike',1,0)
  pdf['zone_bot2'] = pdf['zone_bot']*100
  pdf['zone_top2'] = pdf['zone_top']*100
  pdf['inzone_y'] = np.where((pdf['plate_y']>=pdf['zone_bot2'])&(pdf['plate_y']<=pdf['zone_top2']),1,0)
  pdf['inzone_x'] = np.where((pdf['plate_x']>=70)&(pdf['plate_x']<=140),1,0)
  pdf['InZone2'] = np.where((pdf['inzone_y']==1)&(pdf['inzone_x']==1),1,0)
  pdf['OutZone2'] = np.where(pdf['InZone2']==1,0,1)
  pdf['IsZoneSwing2'] = np.where((pdf['InZone2']==1)&(pdf['SwungOn']==1),1,0)
  pdf['IsChase2'] = np.where((pdf['OutZone2']==1)&(pdf['SwungOn']==1),1,0)
  pdf['IsZoneContact2'] = np.where((pdf['IsZoneSwing2']==1)&(pdf['ContactMade']==1),1,0)

  # HANDLE DUPLICATES
  dupes_hitter_df = pdf.groupby(['BatterName','batter'],as_index=False)['AB'].sum()
  hitter_dupes = dupes_hitter_df.groupby('BatterName',as_index=False)['batter'].count().sort_values(by='batter',ascending=False)
  hitter_dupes = hitter_dupes[hitter_dupes['batter']>1]
  hitter_dupes.columns=['Player','Count']
  hitter_dupes['Pos'] = 'Hitter'
  hitter_dupes_list = list(hitter_dupes['Player'])
  pdf['BatterName'] = np.where(pdf['BatterName'].isin(hitter_dupes_list),pdf['BatterName'] + ' - ' + pdf['batter'].astype(int).astype(str), pdf['BatterName'])

  dupes_pitcher_df = pdf.groupby(['player_name','pitcher'],as_index=False)['PitchesThrown'].sum()
  pitcher_dupes = dupes_pitcher_df.groupby('player_name',as_index=False)['pitcher'].count().sort_values(by='pitcher',ascending=False)
  pitcher_dupes = pitcher_dupes[pitcher_dupes['pitcher']>1]
  pitcher_dupes.columns=['Player','Count']
  pitcher_dupes['Pos'] = 'Pitcher'
  pitcher_dupes_list = list(pitcher_dupes['Player'])
  pdf['player_name'] = np.where(pdf['player_name'].isin(pitcher_dupes_list),pdf['player_name'] + ' - ' + pdf['pitcher'].astype(int).astype(str), pdf['player_name'])

  pdf = dropUnnamed(pdf)
  pdf['game_date'] = pd.to_datetime(pdf['game_date'])
  pdf['player_name'] = pdf['player_name'].replace({'Luis L. Ortiz': 'Luis Ortiz - 682847'})

  # drop dupes
  pdf = pdf.drop_duplicates(subset=['game_pk','pitcher','batter','inning','at_bat_number','pitch_number'])

  return(pdf)

def highlight_rows_sp(row):
    # Example condition: highlight rows where Score > 90
    if row['Current Pitcher?'] == 'Y':
        return ['background-color: lightskyblue'] * len(row)
    else:
        return [''] * len(row)

# Get the directory where the script is located
base_dir = os.path.dirname(__file__)
# Construct the path to the file
file_path = os.path.join(base_dir, 'Files')


# Data Imports
#league_lev_df = pd.read_csv('{}/LeagueLevels.csv')

league_lev_df = pd.read_csv('{}/LeagueLevels.csv'.format(file_path))
#league_lev_df = pd.read_csv('/Users/jonanderson/Desktop/Python/MLBGameScraping/Files/LeagueLevels.csv')
levdict = dict(zip(league_lev_df.league_name,league_lev_df.level))

affdf = pd.read_csv('{}/Team_Affiliates.csv'.format(file_path))
affdict = dict(zip(affdf.team_id, affdf.parent_id))
affdict_abbrevs = dict(zip(affdf.team_id, affdf.parent_abbrev))

team_abbrev_look = dict(zip(affdf.team_name,affdf.team_abbrev))
idlookup_df = pd.read_csv('{}/IDLookupTable.csv'.format(file_path))
p_lookup_dict = dict(zip(idlookup_df.MLBID, idlookup_df.PLAYERNAME))

lsaclass = pd.read_csv('{}/lsaclass.csv'.format(file_path))
lsaclass = dropUnnamed(lsaclass)
lsaclass['launch_speed'] = round(lsaclass['launch_speed'],0)
lsaclass['launch_angle'] = round(lsaclass['launch_angle'],0)
lsaclass.columns=['launch_speed_round','launch_angle_round','launch_speed_angle']
#sav24 = pd.read_csv('/content/drive/My Drive/FLB/Data/savant_data/sav2024.csv')

eastern = pytz.timezone('US/Eastern')
now_eastern = datetime.now(eastern)
now_date = now_eastern.date()
today_str = now_date.strftime("%Y-%m-%d")

header_placeholder = st.empty()

today_games = getLiveGames(today_str)
today_games_df = pd.DataFrame(today_games)
today_games_df['game_start_time_et'] = pd.to_datetime(today_games_df['game_start_time']).dt.tz_convert('US/Eastern')

today_games_df['game_time'] = pd.to_datetime(today_games_df['game_start_time_et']).dt.strftime('%I:%M %p')

show_sched = today_games_df[['date','game_time','away_team','home_team','game_status']]
show_sched.columns=['Date','Time','Away','Home','Status']
show_sched = show_sched[show_sched['Status']=='I']
st.dataframe(show_sched,hide_index=True, width=800, height=200)

# Create placeholders for the DataFrames
st.write('Pitcher Data:')
df1_placeholder = st.empty()

#### MESSING AROUND WITH COLUMNS ####
# Create two columns
col1, col2 = st.columns(2)


# Put placeholders in columns
with col1:
   st.write('Homers:')
   df2_placeholder = st.empty()
   #st.placeholder1 = st.empty()  # Placeholder in column 1

with col2:
   st.write('Top EVs:')
   df3_placeholder = st.empty()

#st.write('Homers:')
#df2_placeholder = st.empty()
#st.write('Top EVs:')
#df3_placeholder = st.empty()

#################

while True:
    eastern = pytz.timezone('US/Eastern')
    import datetime
    now_eastern = datetime.datetime.now(eastern)
    current_time = now_eastern.strftime("%I:%M")
    header_placeholder.title('@JonPGH Live MLB Game Data (last update: {})'.format(current_time))

    ###### CHECK FOR GAMES ######
    gameslive = 'N'
    while gameslive != 'Y':
      today_games = getLiveGames(today_str)
      
      gamestatuslist = []
      for game in today_games:
          game_status = game.get('game_status')
          gamestatuslist.append(game_status)


      if ('I' not in gamestatuslist) and ('S' not in gamestatuslist) and ('P' not in gamestatuslist):
         st.write('All games today are complete.')
         st.stop()

      if 'I' not in gamestatuslist:
          if 'I' not in gamestatuslist:
              st.write('No live games, but more coming, waiting 10 minutes')
              gameslive = 'N'
              time.sleep(60*10)
          pass
      else:
          gameslive = 'Y'

    #######################
    livedb = pd.DataFrame()
    #st.write('FOUND LIVE GAME!')
    for game in today_games:
        game_status = game.get('game_status')
        if game_status != 'I':
           continue
        
        gamedb = get_MILB_PBP_Live(game)

        if len(gamedb) == 0:
            pass
        else:
            if gamedb['StatcastGame'].iloc[0] == 'Y':
                gamedb['game_status'] = game_status
                livedb = pd.concat([livedb,gamedb])
            else:
                pass

        if len(livedb)==0:
            continue
        livedb = savAddOns(livedb)

        finishedgames = livedb[livedb['game_status']=='F']
        finished_game_pitchers = list(finishedgames['player_name'].unique())
        #pitchergamestatus = dict(zip(livedb.player_name,livedb.game_status))

        lastpitcher = livedb.sort_values(by=['inning','at_bat_number','pitch_number'])[['PitcherTeam_aff','player_name','inning','at_bat_number','pitch_number']]
        cutlist=lastpitcher[['PitcherTeam_aff','player_name']].drop_duplicates()
        currentpitchers = cutlist.drop_duplicates(subset=['PitcherTeam_aff'],keep='last')
        cplist_1 = list(currentpitchers['player_name'])

        cplist = []
        for cp in cplist_1:
            if cp in finished_game_pitchers:
                pass
            else:
                cplist.append(cp)

        livedb['DP'] = np.where((livedb['play_desc'].str.contains('double play'))&(livedb['PA_flag']==1),1,0)

        pdata = livedb.groupby(['player_name','pitcher','PitcherTeam_aff'],as_index=False)[['PitchesThrown','IsStrike','IsBall','IsBIP','IsHit','IsHomer','IsSwStr','IsGB','IsLD','IsFB','IsBrl','PA_flag','DP','IsStrikeout','IsWalk']].sum()
        pdata['Outs'] = pdata['PA_flag']-pdata['IsHit']-pdata['IsWalk']+pdata['DP']
        pdata['IP'] = round((pdata['Outs']/3),2)
        pdata['SwStr%'] = round(pdata['IsSwStr']/pdata['PitchesThrown'],3)
        pdata['Strike%'] = round(pdata['IsStrike']/pdata['PitchesThrown'],3)
        pdata['Ball%'] = round(pdata['IsBall']/pdata['PitchesThrown'],3)
        pdata['GB%'] = round(pdata['IsGB']/pdata['IsBIP'],3)
        pdata['FB%'] = round(pdata['IsFB']/pdata['IsBIP'],3)
        pdata['LD%'] = round(pdata['IsLD']/pdata['IsBIP'],3)
        pdata['Brl%'] = round(pdata['IsBrl']/pdata['IsBIP'],3)

        pdata = pdata.sort_values(by='IsSwStr',ascending=False)
        pdata = pdata[['player_name','pitcher','PitcherTeam_aff','PA_flag','IP','IsStrikeout','IsWalk','IsHit','IsHomer','PitchesThrown','IsSwStr','IsStrike','SwStr%','Strike%','Ball%','GB%','LD%','FB%','Brl%']]
        pdata.columns=['Pitcher','ID','Team','TBF','IP','SO','BB','H','HR','PC','Whiffs','Strikes','SwStr%','Strike%','Ball%','GB%','LD%','FB%','Brl%']
        pdata['Current Pitcher?'] = np.where(pdata['Pitcher'].isin(cplist),'Y','N')
        showdf = pdata.copy()
        df = showdf[['Pitcher','Team','IP','PC','SO','BB','Whiffs','SwStr%','Strike%','Ball%','Current Pitcher?']].sort_values(by=['Whiffs'],ascending=False)
        df['SwStr%'] = round(df['SwStr%'],3)
        df['Strike%'] = round(df['Strike%'],3)
        df['Ball%'] = round(df['Ball%'],3)
        df['IP'] = round(df['IP'],1)


        ## Hitter stuff
        hrs = livedb[livedb['IsHomer']==1][['BatterName','BatterTeam_aff','player_name','launch_speed','play_desc']].sort_values(by='launch_speed',ascending=False)
        hrs.columns=['Hitter','Team','Pitcher','EV','Description']
        
        evs = livedb[['BatterName','BatterTeam_aff','player_name','launch_speed','play_desc']].sort_values(by='launch_speed',ascending=False)
        evs.columns=['Hitter','Team','Pitcher','EV','Description']
    
    #df = pd.DataFrame({'Pitcher': ['Pitcher1','Pitcher2','Pitcher3'], 'Team': ['STL','PIT','CHC'],
    #                       'PC': [10,15,20], 'SO': [1,2,3],
    #                       'BB': [1,2,3], 'Whiffs': [1,2,3], 'SwStr%': [.1,.11,.12], 'Current Pitcher?': ['Y','N','N']})
    #hrs = pd.DataFrame({'BatterName': 'Luis Robert', 'BatterTeam_aff': 'CWS', 'player_name': 'Mitch Keller', 'launch_speed': 105, 'play_desc': 'desecription'}, index=[0])
    #st.dataframe(df,hide_index=True, width=800, height=200)
    
    df['IP'] = round(df['IP'],1)
    df['SwStr%'] = round(df['SwStr%'],3)
    styled_df = df.style.apply(highlight_rows_sp, axis=1)
    #styled_df['SwStr%'] = round(styled_df['SwStr%'],3)
    #styled_df['Strike%'] = round(styled_df['Strike%'],3)
    #styled_df['Ball%'] = round(styled_df['Ball%'],3)
    #styled_df['IP'] = round(styled_df['IP'],1)


    try:
       df1_placeholder.dataframe(df,width=800, height=200, hide_index=True)
    except:
       pass
    try:
       df2_placeholder.dataframe(hrs,width=800, height=200, hide_index=True)
    except:
       pass
    try:
       df3_placeholder.dataframe(evs,width=800, height=200, hide_index=True)
    except:
       pass
    
    print('waiting 30 seconds to refresh')
    time.sleep(30)
    
    #try:
      #df1_placeholder.dataframe(df, hide_index=True)
      #time.sleep(30)
    #except:
       #st.write('No game data to display')   

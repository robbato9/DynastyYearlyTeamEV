# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



from sleeper_wrapper import League
import pandas as pd
from sleeper_wrapper import Stats
from sleeper_wrapper import Players



def weekly_stats(wk, league): 
    stats = Stats()
    
    t = stats.get_week_projections('regular', 2021, wk)
    stats_df = pd.DataFrame.from_dict(t, orient = 'index')
    
    roster = league.get_rosters()
    roster_df = pd.DataFrame(roster)
    rdf_sub = roster_df[['owner_id', 'players']]
    
    owner_df = rdf_sub.set_index('owner_id').players.apply(pd.Series).stack().reset_index(level=0).rename(columns={0:'players'})
    
    stats_df.reset_index(inplace = True)
    
    stat_sub = stats_df[['index', 'pts_half_ppr']]
    stat_sub.columns = ['players', 'half_ppr_expected_pts']
    
    ow_st_merge = pd.merge(owner_df, stat_sub, on='players', how='left')
    
    players = Players()
    player_df = pd.DataFrame.from_dict(players.get_all_players(), orient='index')
    player_sub = player_df[['player_id', 'position', 'first_name', 'last_name']]
    player_sub.columns = ['players', 'position', 'first_name', 'last_name']
    
    pl_ow_st = pd.merge(ow_st_merge, player_sub, on = 'players', how = 'left')
    return pl_ow_st



def find_best_team(df, pos, flex_opt = None, super_flex = None):
    df_cp = df.copy(deep = True)
    team = []
    for p in pos:
        if(p == 'flex'):
            pos_sub = df_cp.loc[df['position'].isin(flex_opt)]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
        elif(p == 'superflex'):
            pos_sub = df_cp.loc[df['position'].isin(super_flex)]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
        else:            
            pos_sub = df_cp.loc[df['position'] == p]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
    return pd.DataFrame(team), df_cp

def leftover_build(df, pos, flex_opt = None, super_flex = None):
    df_cp = df.copy(deep = True)
    team = []
    for p in pos:
        if(p == 'flex'):
            pos_sub = df_cp.loc[df['position'].isin(flex_opt)]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
        elif(p == 'superflex'):
            pos_sub = df_cp.loc[df['position'].isin(super_flex)]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
        else:            
            pos_sub = df_cp.loc[df['position'] == p]
            pos_sub.sort_values('half_ppr_expected_pts', ascending = False, inplace = True)
            team.append(pos_sub.iloc[0])
            df_cp.drop(pos_sub.iloc[0].name,  inplace=True)
    return pd.DataFrame(team)

def best_team_partial_rfa(df, pos= ['QB', 'WR', 'RB', 'TE'], flex_opt = None, super_flex = None):
    df_cp = df.copy(deep = True)
    df_cp.sort_values('half_ppr_expected_pts', ascending = False, 
                            inplace = True)
    players = []
    for p in pos:
        if(p == 'flex'):
            t = df_cp[df_cp.position.isin(flex_opt)].iloc[0]
            players.append(t)
            df_cp.drop(t.name, inplace = True)
        elif(p == 'superflex'):
            t = df_cp[df_cp.position.isin(super_flex)].iloc[0]
            players.append(t)
            df_cp.drop(t.name, inplace = True)
        else:
            players.append(df_cp[df_cp.position == p].iloc[0])
            df_cp.drop(df_cp[df_cp.position ==p ].iloc[0].name,  inplace=True)

    
    return pd.DataFrame(players), df_cp
        
    

lid = 656332800647081984
league = League(lid)
roster = league.get_rosters()
users = pd.DataFrame(league.get_users())
user_sub = users[['user_id', 'display_name']]  
flex = ['RB', 'WR', 'TE']
superflex = ['QB', 'RB', 'WR', 'TE']
positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'superflex', 'flex']


def full_rfa():
    lid = 656332800647081984
    league = League(lid)
    users = pd.DataFrame(league.get_users())
    user_sub = users[['user_id', 'display_name']]  
    flex = ['RB', 'WR', 'TE']
    superflex = ['QB', 'RB', 'WR', 'TE']
    positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'superflex', 'flex']

    weekly_dfs = []
    for i in range(1, 18):
        wstat = weekly_stats(i, league)
        best_teams = []
        leftover = []
        for i1, x in wstat.groupby('owner_id'):
            best_teams.append(find_best_team(x, positions, flex, superflex)[0])
            leftover.append(find_best_team(x, positions, flex, superflex)[1])
        
        weekly_leftover = pd.concat(leftover)
        leftover_best = []
        int_df, leftover2 = find_best_team(weekly_leftover, positions, flex, superflex)
        int_df['display_name'] = 1
        leftover_best.append(int_df)
        
        int_df2 =  find_best_team(leftover2, positions, flex, superflex)[0]
        int_df2['display_name'] = 2
        leftover_best.append(int_df2)
    
        best_usr_pts = pd.concat(best_teams)
        leftover_pts = pd.concat(leftover_best)
        
        best_pts = pd.concat([best_usr_pts,leftover_pts], sort = True)
        
        final = pd.merge(user_sub, best_pts, left_on = 'user_id', right_on = 'owner_id', 
                         how = 'outer')
    
        
        final['dname'] = final['display_name_y'].fillna(final['display_name_x'])
    
    
        df = final.groupby('dname')['half_ppr_expected_pts'].mean().reset_index()
        df['half_ppr_ex_ppw'] = df['half_ppr_expected_pts']*8
        df['week'] = i
        weekly_dfs.append(df)
        
    final_df = pd.concat(weekly_dfs)
    final_df.to_csv(r'C:\Users\robba\Desktop\weekly_wSuperFlex.csv')
    
    
def partial_rfa():
    lid = 656332800647081984
    league = League(lid)
    users = pd.DataFrame(league.get_users())
    user_sub = users[['user_id', 'display_name']]  
    flex = ['RB', 'WR', 'TE']
    superflex = ['QB', 'RB', 'WR', 'TE']
    positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'superflex', 'flex']
    weekly_dfs = []
    for i in range(1, 18):
        wstat = weekly_stats(i, league)
        best_teams = []
        leftover = []
        for i1, x in wstat.groupby('owner_id'):
            t = best_team_partial_rfa(x, ['QB', 'WR', 'RB', 'TE', 'superflex', 'flex'],  flex, superflex)
            best_teams.append(t[0])
            leftover.append(t[1])
        
        weekly_leftover = pd.concat(leftover)
        leftover_best = []
        int_df, leftover1 = find_best_team(weekly_leftover, positions, flex, superflex)
        int_df['display_name'] = 1
        leftover_best.append(int_df)
        
        int_df2, leftover2 =  find_best_team(leftover1, positions, flex, superflex)
        int_df2['display_name'] = 2
        leftover_best.append(int_df2)
        for i2, x2 in leftover2.groupby('owner_id'):
            rest_pos = ['RB', 'WR']
            best_teams.append(best_team_partial_rfa(x2, rest_pos,  flex, superflex)[0])
            
    
        best_usr_pts = pd.concat(best_teams)
        leftover_pts = pd.concat(leftover_best)
        best_pts = pd.concat([best_usr_pts,leftover_pts], sort = True)
        
        final = pd.merge(user_sub, best_pts, left_on = 'user_id', right_on = 'owner_id', 
                         how = 'outer')
    
        
        final['dname'] = final['display_name_y'].fillna(final['display_name_x'])
    
    
        df = final.groupby('dname')['half_ppr_expected_pts'].mean().reset_index()
        df['half_ppr_ex_ppw'] = df['half_ppr_expected_pts']*8
        df['week'] = i
        weekly_dfs.append(df)
        
        print('Week ' + str(i) + ' done')
    final_df = pd.concat(weekly_dfs)
    final_df.to_csv(r'C:\Users\robba\Desktop\weekly_wSuperFlex_6RFA.csv')
    
partial_rfa()





    
            






from ..constants import tracker_columns
import colorama as cl
import pandas as pd

class Function_Dictionary_Class:

    date_highlight_thresholds = [
        [pd.Timedelta(days=30), cl.Fore.GREEN],
        [pd.Timedelta(days=7),  cl.Fore.YELLOW],
        [pd.Timedelta(hours=2), cl.Fore.RED],
    ]

    def update(self, **kwargs):
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

def transform_dataframe(input_df):
    #Remove all non-numeric digits
    input_df = input_df.replace("[,s\%]", "", regex=True)
    
    input_df = input_df[tracker_columns.float_columns].astype(float)

    #Recalculate win percentage
    input_df[tracker_columns.win_perc] = input_df[tracker_columns.wins] / (input_df[tracker_columns.wins] + input_df[tracker_columns.losses] + input_df[tracker_columns.ties])

    return input_df

def highlight_dataframe(input_df, reference_df, upper_quantile=0.9, lower_quantile=0.1):
    top_quantiles = reference_df.quantile(q=upper_quantile)
    bot_quantiles = reference_df.quantile(q=lower_quantile)

    for col in top_quantiles.index:
        if col == "times_played":
            continue

        try:
            input_df.loc[input_df[col] >= top_quantiles[col]] = cl.Fore.WHITE + cl.Back.RED   + input_df[col].astype(str) + cl.Style.RESET_ALL
            input_df.loc[input_df[col] <= bot_quantiles[col]] = cl.Fore.WHITE + cl.Back.GREEN + input_df[col].astype(str) + cl.Style.RESET_ALL
        except (KeyError, ValueError):
            continue
    
    return input_df

def last_seen_formatter(timedelta):
    try:
        components_dict = timedelta.components._asdict()
    except AttributeError:
        if timedelta[-3:] == "ago":
            return timedelta
        else:
            try:
                components_dict = pd.to_timedelta(timedelta).components._asdict()
            except ValueError:
                return timedelta

    for unit_of_time in components_dict.keys():
        value   = components_dict[unit_of_time]
        if value > 0:
            return f"{value} {unit_of_time} ago"

def display_dataframe(input_df):
    input_df['Name']        = input_df['Name'].str[-25:]
    input_df['Controller']  = input_df['Controller'].str[:4]

    played_ser = (pd.Timestamp.now() - input_df['last_played'] + pd.Timedelta(hours=5)).fillna(pd.Timedelta(days=9999))
    input_df['last_played'] = played_ser

    for i, [threshold, color] in enumerate(func_dict.date_highlight_thresholds):
        
        if i < len(func_dict.date_highlight_thresholds) - 1:
            condition = (played_ser <= threshold) & (played_ser > func_dict.date_highlight_thresholds[i+1][0])
        else:
            condition = played_ser <= threshold

        last_seen_string = input_df.loc[condition, 'last_played'].apply(last_seen_formatter)
        if len(last_seen_string) == 0:
            continue
        input_df.loc[condition, 'last_played'] = color + last_seen_string + cl.Style.RESET_ALL
    
    input_df.loc[played_ser > func_dict.date_highlight_thresholds[0][0], "last_played"] = input_df.loc[played_ser > func_dict.date_highlight_thresholds[0][0], "last_played"].apply(last_seen_formatter)

    input_df['last_played'] = input_df['last_played'].replace({pd.Timedelta(days=9999): None})

    input_df['K/D Ratio'] = input_df['K/D Ratio'].apply(lambda x: "{: .3f}".format(x))
    low_kdr_condition   = input_df['K/D Ratio'].astype(float) <= 0.7
    high_kdr_condition  = input_df['K/D Ratio'].astype(float) >= 1.8
    input_df.loc[low_kdr_condition, 'K/D Ratio']    = cl.Fore.GREEN + input_df.loc[low_kdr_condition, 'K/D Ratio'] + cl.Style.RESET_ALL
    input_df.loc[high_kdr_condition, 'K/D Ratio']   = cl.Fore.WHITE + cl.Back.RED + input_df.loc[high_kdr_condition, 'K/D Ratio'] + cl.Style.RESET_ALL

    return input_df
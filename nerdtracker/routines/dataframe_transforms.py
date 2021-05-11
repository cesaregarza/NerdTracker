from ..constants import tracker_columns

def transform_dataframe(input_df):
    #Remove all non-numeric digits
    input_df = input_df.replace("[,s\%]", "", regex=True)
    
    input_df = input_df[tracker_columns.float_columns].astype(float)

    #Recalculate win percentage
    input_df[tracker_columns.win_perc] = input_df[tracker_columns.wins] / (input_df[tracker_columns.wins] + input_df[tracker_columns.losses] + input_df[tracker_columns.ties])

    return input_df

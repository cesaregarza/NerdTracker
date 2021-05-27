import pandas as pd
import socket
from ...constants import tracker_columns
import datetime as dt


def submit_dataframe(sql_engine, dataframe: pd.DataFrame):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    #Remove any names not matched. Temporary solution.
    submit_df               = dataframe.loc[~dataframe[tracker_columns.kdr].isna()].copy()

    #Add the timestamp, as well as the IP address
    submit_df["Timestamp"]  = dt.datetime.now()
    submit_df["IP Address"] = ip_address

    submit_df.to_sql("tracked_nerds", sql_engine, if_exists="append")
    print("Successfully wrote to database")
    return
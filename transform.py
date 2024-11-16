import pandas as pd

def col_to_date(df_extract, date_cols): #Convert columns to datetime type
    for col in date_cols:
        df_extract[col] = pd.to_datetime(df_extract[col])
    return df_extract


def filter_selected_day(df_extract_1, date_col, day_range): # Filter the day range from user input
    df_extract = df_extract_1.copy()
    df_extract = df_extract[(df_extract[date_col].dt.day >= day_range[0]) &
                        (df_extract[date_col].dt.day <= day_range[1])]
    
    return df_extract

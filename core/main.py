from src.db_conn import DatabaseConnection
from src.models import SarimaxModel
from src.cleaner import Cleaner
from config.settings import (
    DB_HOST,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT,
    DB_USER,
    SSH_IP,
    SSH_PRIVATE_KEY,
    SSH_USERNAME,
    SSH_PORT,
    DATA_DIR,
    FORECAST_DIR,
    MODELS_DIR
)
import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


def main(*,
         train_from: str = None,
         train_to: str = None,
         start_pred: str = None,
         end_pred: str = None
         ):

    #instance a new database connection
    db_conn = DatabaseConnection(
        DB_HOST=DB_HOST,
        DB_NAME=DB_NAME,
        DB_PASSWORD=DB_PASSWORD,
        DB_PORT=DB_PORT,
        DB_USER=DB_USER,
        SSH_PRIVATE_KEY=SSH_PRIVATE_KEY,
        SSH_IP=SSH_IP,
        SSH_USERNAME=SSH_USERNAME,
        SSH_PORT=SSH_PORT
        )

    #set the query to bring sales data
    sales_query = """
    SELECT sale_date, net_price, route_id FROM sale_transactions
    """
    #fix output path
    save_as_sales_query = input('query was executed successfully. how do you want to save the generated csv: ')
    output_path = f'{DATA_DIR}/{save_as_sales_query}.csv'


    #convert query to a csv and convert it as a df
    sales = db_conn.query_to_csv(query=sales_query, output_file_name=output_path)
    sales['route_id'] = sales['route_id'].astype('Int64').astype(str)


    #instance the claner
    cleaner = Cleaner()
    print('\nCleaner object was instanced successfully\n')

    #prepare data and get it filtered
    exclude_raw = input('exclude routes (separated by comma, e.g.: 90, 95) [press enter for none]: ')
    exclude_routes = [r.strip() for r in exclude_raw.split(',')] if exclude_raw.strip() else []

    include_raw = input('include routes (separated by comma, e.g.: 90, 95) [press enter for all]: ')
    include_routes = [r.strip() for r in include_raw.split(',')] if include_raw.strip() else []

    data = cleaner.prepare_data(data=sales, exclude_routes=exclude_routes, include_routes=include_routes)
    print('\nprepare_data method was applied on base Dataframe\n')

    #get the serie whcih is gonna be consumed by the model
    target_input = input('please enter the target column name (y) [enter for "net_price"]: ').strip()
    y_column = target_input if target_input else 'net_price'

    date_input = input('please enter the date column name (index) [enter for "sale_date"]: ').strip()
    datetime_column = date_input if date_input else 'sale_date'

    series = cleaner.daily_grouper(raw_data=data, y=y_column, datetime_col=datetime_column)
    print(f'\n{y_column} as pd.Series object was created successfully\n')

    #remove outliers
    outlier_mask = series < 0

    valid_methods = ['set_nan', 'drop', 'linear', 'neighbor_average', 'zero', 'ffill']
    
    while True:
        print(f"\navailable methods: {', '.join(valid_methods)}")
        method_input = input('select a method to remove outliers [press enter for "linear"]: ').strip()
        
        chosen_method = method_input if method_input else 'linear'
        
        if chosen_method in valid_methods:
            break
        else:
            print(f"'{chosen_method}' is not a avlid option. please write one of the list")

    series = cleaner.delete_outliers_method(
        series=series, 
        outlier_mask=outlier_mask, 
        method=chosen_method
    )
    print(f'\noutliers was removed from pd.Series using method: {chosen_method}\n')

    min_date_db = series.index.min().strftime('%Y-%m-%d')
    max_date_db = series.index.max().strftime('%Y-%m-%d')

    print("\ntraining range dates")
    in_train_from = input(f'start training from [Enter for {min_date_db}]: ').strip()
    train_from_secure = in_train_from if in_train_from else min_date_db

    in_train_to = input(f'end training on [Enter for {max_date_db}]: ').strip()
    train_to_secure = in_train_to if in_train_to else max_date_db

    series = series.loc[train_from_secure:train_to_secure]

    print(f'\nData was converted into pd.Series (Range: {train_from_secure} a {train_to_secure})\n')
    print(series.head())

    # instance model
    model = SarimaxModel(data=series)

    #define list of holidays
    base_non_work_days = []
    try:
        with open(f'{MODELS_DIR}/non_business_days/non_business_days.json', "r", encoding="utf-8") as f:
            holidays_data = json.load(f)
        years_dict = holidays_data.get("base_non_work_days", {})
        for year, festivities in years_dict.items():
            base_non_work_days.extend(festivities.values())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error while loading json ({e}). Empty list will be used in place.")

    print('\nNon business days to use\n')
    print(base_non_work_days)



    #generate exog for training
    X_exog = model.generate_exog_matrix(start_date=train_from_secure, end_date=train_to_secure, holidays_source=base_non_work_days)
    X_exog = X_exog[['is_month_end', 'close_month_zone']]

    fit_model, metadata_model, meta_id = model.train_sarimax(
        train_from=train_from_secure,
        train_to=train_to_secure,
        endog=series,
        exog = X_exog,
    )

    print(f'\n{metadata_model}')



    print("\nforecast range dates")

    today = datetime.now().date()
    one_month_from_now = today + relativedelta(month=1)

    in_start_pred = input(f'start forecast from [Enter for {today}]: ').strip()
    start_pred_secure = in_start_pred if in_start_pred else today

    in_end_pred = input(f'end forecast on [Enter for {one_month_from_now}]: ').strip()
    end_pred_secure = in_end_pred if in_end_pred else one_month_from_now

    forecast = model.run_sarimax(
        predict_from=start_pred_secure,
        predict_to=end_pred_secure,
        y=series,
        X_exog=X_exog,
        holidays=base_non_work_days,
        params_id=meta_id
    )

    print('forecast made successful')

    print(f'Forecast for period {start_pred} - {end_pred}: {forecast['forecast'].sum()}')

    save_as = input('Save file output with predictions as: ')

    forecast.to_csv(f'{FORECAST_DIR}/{save_as}.csv')

    pass
    


    





if __name__ == '__main__':
    main()










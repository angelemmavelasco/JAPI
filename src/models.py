import json
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
import os
import uuid
from datetime import datetime
import calendar
from typing import Union, List, Tuple

from config.settings import (
    MODELS_DIR,
)


class SarimaxModel:

    def __init__(self, *, data: pd.Series):
        self.data = data

    def save_metadata(self,*,
                  order: list = [0,0,0],
                  seasonal_order: list = [0,0,0,7],
                  enforce_stationarity: bool = False,
                  enforce_invertibility: bool = False,
                  fit_obj,
                  file_path: str = f'{MODELS_DIR}/sarimax.json',
                  model_id: str = None,
                  ) -> dict:
        
        """
        Save the training results in a json file set within the params.

        """

        try:
            start_date = fit_obj.model.data.dates[0].strftime('%Y-%m-%d')
            end_date = fit_obj.model.data.dates[-1].strftime('%Y-%m-%d')
        except (AttributeError, TypeError):
            start_date = str(fit_obj.model.data.row_labels[0])
            end_date = str(fit_obj.model.data.row_labels[-1])

        coefs_clean = {k: float(v) for k, v in fit_obj.params.to_dict().items()}

        model_metadata = {
            "train_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "hyperparameters": {
                "order": order,
                "seasonal_order": seasonal_order,
                "enforce_stationarity": enforce_stationarity,
                "enforce_invertibility": enforce_invertibility
            },
            "metrics": {
                "aic": float(fit_obj.aic),
                "bic": float(fit_obj.bic),
                "log_likelihood": float(fit_obj.llf),
                "nobs": int(fit_obj.nobs)
            },
            "coeficientes": coefs_clean
        }

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data_historica = json.load(f)
                except json.JSONDecodeError:
                    data_historica = {}
        else:
            data_historica = {}

        if model_id is None:
            model_id = f'{datetime.now().date()}_{uuid.uuid4()}'

        data_historica[model_id] = model_metadata

        with open(file_path, "w") as f:
            json.dump(data_historica, f, indent=4)

        print(f'Metadata saved for model: {model_id}\n')
        return model_metadata, model_id

    def get_model_metadata(self, *,
                            params_id: str = None,
                            file_path: str = f"{MODELS_DIR}/sarimax.json") -> dict:
        """
        Retrieves the metadata of a specific model by ID or selects the best model from the registry.

        If a specific `params_id` is provided, it performs a direct lookup in the registry. 
        If no ID is supplied, the method automatically scans the registry to select the "best" 
        model based on a two-tier optimization process: first, it prioritizes the model trained 
        on the most recent data (`end_date`); second, in case of a tie in dates, it selects 
        the model with the lowest Akaike Information Criterion (`aic`).

        Parameters
        ----------
        params_id : str, optional
            The unique identifier of the registered model configuration to look up. 
            If None, the method executes the selection logic for the best model. Default is None.
        file_path : str, optional
            The filesystem path to the JSON file acting as the model registry. 
            Default is '{MODELS_DIR}/sarimax.json'.

        Returns
        -------
        dict
            A dictionary containing the metadata of the selected model (including training 
            periods, parameters, and metrics).

        Raises
        ------
        FileNotFoundError
            If the registry file does not exist at the specified `file_path`.
        ValueError
            If the JSON file is successfully loaded but contains no data (empty registry).
        KeyError
            If a specific `params_id` was requested but is not found within the registry keys.
        """
        
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File of models {file_path} does not exist.")
            
        with open(file_path, "r") as f:
            model_registry = json.load(f)
            
        if not model_registry:
            raise ValueError("Model file is empty.")


        if params_id is not None:
            if params_id not in model_registry:
                raise KeyError(f"Model Id '{params_id}' is not registered.")
            return model_registry[params_id]


        best_model = None
        latest_date = "1900-01-01"
        lowest_aic = float('inf')

        for model_key, meta in model_registry.items():
            current_end_date = meta["train_period"]["end_date"]
            current_aic = meta["metrics"]["aic"]

            if current_end_date > latest_date:
                latest_date = current_end_date
                lowest_aic = current_aic
                best_model = meta

            elif current_end_date == latest_date:
                if current_aic < lowest_aic:
                    lowest_aic = current_aic
                    best_model = meta

        return best_model
    
    def generate_exog_matrix(self, *,
                              start_date: str,
                              end_date: str,
                              holidays_source: Union[str, list] = None) -> pd.DataFrame:
        """
        Generate an Exogenous Matrix for a date range independently.

        Parameters
        ----------
        start_date : str
            Start date of the range ('yyyy-mm-dd').
        end_date : str
            End date of the range ('yyyy-mm-dd').
        holidays_source : str or list, optional
            Path to the JSON file containing 'base_non_work_days' with nested years,
            or a direct list of date strings.
        
        Returns
        -------
        pd.DataFrame
            Exogenous matrix with 'non_work_day', 'is_month_end' and 'close_month_zone' features.
        """
        
        base_non_work_days = []

        #if holidays source is a path
        if isinstance(holidays_source, str):
            #open json file
            try:
                with open(holidays_source, "r", encoding="utf-8") as f:
                    holidays_data = json.load(f)
                
                #get dict indexed by year
                # {
                # "base_non_work_days": {
                #     "2024": {
                #     "Año Nuevo": "2024-01-01",
                #     "Natalicio de Benito Juárez": "2024-03-18",
                #     "Jueves Santo": "2024-03-28",

                years_dict = holidays_data.get("base_non_work_days", {})
                
                for year, festivities in years_dict.items():
                    base_non_work_days.extend(festivities.values())
                    
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error while loading json ({e}). Empty list will be used in place.")
        
        #if list is directly provided, that would be used
        elif isinstance(holidays_source, list):
            base_non_work_days = holidays_source

        #set the range of dates
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        #define exog matrix with date range as index
        X_exog = pd.DataFrame(index=future_dates)
        
        #delete duplicated values in th elist of dates
        all_non_work_days = list(set(base_non_work_days))

        X_exog['non_work_day'] = X_exog.index.strftime('%Y-%m-%d').isin(all_non_work_days).astype(int)
        is_weekend = X_exog.index.weekday.isin([5, 6])
        X_exog['is_workday'] = ~(is_weekend | (X_exog['non_work_day'] == 1))
        
        X_exog['is_month_end'] = 0
        X_exog['close_month_zone'] = 0
        
        #get close zone and is month end
        for period, group in X_exog.groupby(X_exog.index.to_period('M')):
            work_days_month = group[group['is_workday']].index
            
            if len(work_days_month) >= 1:
                X_exog.loc[work_days_month[-1], 'is_month_end'] = 1
            
            if len(work_days_month) >= 3:
                X_exog.loc[work_days_month[-3:-1], 'close_month_zone'] = 1
            elif len(work_days_month) == 2:
                X_exog.loc[work_days_month[0], 'close_month_zone'] = 1
        
        return X_exog

    def run_sarimax(self, *,
                            params_id: str = None,
                            predict_from: str,
                            predict_to: str,
                            y: pd.Series = None,
                            X_exog: pd.DataFrame = None,
                            holidays: list = None
                            ):
            
        if y is not None:
            y = y.astype(float)
            y_scaled = y/1000000
            
        if X_exog is not None:
            X_exog = X_exog.astype(float)

        #extract the best model based on an id or by searching
        meta = self.get_model_metadata(params_id=params_id)
            
        model = SARIMAX(
            endog=y_scaled,
            exog=X_exog,
            order=tuple(meta["hyperparameters"]["order"]),
            seasonal_order=tuple(meta["hyperparameters"]["seasonal_order"]),
            enforce_stationarity=meta["hyperparameters"]["enforce_stationarity"],
            enforce_invertibility=meta["hyperparameters"]["enforce_invertibility"]
        )
            
        ordered_params = [meta["coeficientes"][name] for name in model.param_names]
            
        #generate exog for future
        X_exog_future = self.generate_exog_matrix(start_date=predict_from, end_date=predict_to, holidays_source=holidays)
        X_exog_future = X_exog_future[['is_month_end', 'close_month_zone']]
        #which is gonna be the predicted horizon
        fitted_model = model.filter(ordered_params)
        
        prediction_obj = fitted_model.get_prediction(
            start=predict_from, 
            end=predict_to, 
            exog=X_exog_future
        )
        
        result = pd.DataFrame({
            'forecast': prediction_obj.predicted_mean,
            'lower_ci': prediction_obj.conf_int(alpha=0.05).iloc[:, 0],
            'upper_ci': prediction_obj.conf_int(alpha=0.05).iloc[:, 1]
        })
        
        result.index.name = 'date'
        
        return result
    
    def train_sarimax(
            self, *,
            train_from: str = None,
            train_to: str = None,
            endog: pd.Series = None,
            exog: pd.DataFrame = None,
            ar_order: Tuple[int, int, int] = (1, 0, 0),
            s_order: Tuple[int, int, int, int] = (0, 1, 1, 7),
            enforce_stationarity: bool = False,
            enforce_invertibility: bool = False
    ):
        if endog is None:
            raise ValueError('endog parameter (y) must be provided.')
        
        endog = endog/1000000
        
        if not isinstance(endog.index, pd.DatetimeIndex):
            raise TypeError("endog.index must be provided as pd.DatetimeIndex type")
        
        train_from_secure = train_from if train_from else endog.index.min()
        train_to_secure = train_to if train_to else endog.index.max()
        endog_trimmed = endog.loc[train_from_secure:train_to_secure]
        
        exog_trimmed = None
        if exog is not None:
            if not isinstance(exog.index, pd.DatetimeIndex):
                raise TypeError("exog.index must be provided as pd.DatetimeIndex type")
            exog_trimmed = exog.loc[train_from_secure:train_to_secure]
            
            if exog_trimmed.isna().any().any():
                raise ValueError("exog contains NaNs values")

        if endog_trimmed.index.freq is None:
            endog_trimmed.index.freq = pd.infer_freq(endog_trimmed.index)
        if exog_trimmed is not None:
            exog_trimmed.index.freq = endog_trimmed.index.freq

        model = SARIMAX(
            endog=endog_trimmed,
            exog=exog_trimmed,
            order=ar_order,
            seasonal_order=s_order,
            enforce_stationarity=enforce_stationarity,
            enforce_invertibility=enforce_invertibility
        )

        fit = model.fit(disp=False)
        print(fit.summary())

        meta, meta_id = self.save_metadata(
            order=list(ar_order),
            seasonal_order=list(s_order),
            fit_obj=fit,
            
        )

        return fit, meta, meta_id


    




import pandas as pd
from typing import Literal
import numpy as np

class Cleaner:
    def __init__(self):
        pass

    def daily_grouper(self, *,
                    raw_data: pd.DataFrame = None,
                    y: str= 'net_price',
                    datetime_col: str = 'sale_date'
                    ) -> pd.Series:
        
        """
        Converts a Dataframe into a Series grouped by daily frequency.

        Parameters
        ----------
        raw_data : pd.Dataframe
            Contains the raw data. This includes target columns (y) and datetime column which is going to be grouped by Day
        y : str
            The name of the column which is going to be predicted by the model
        datetime_col : str
            Column which contains the datetime data to be grouped by day. The format of this parameter is 'yyyy-mm-dd'
        
        Returns
        -------
        pd.Series
            A pandas Series with index defined as datetime with daily frequency and the sum of y as Value.
        """

        if raw_data is None:
            raise ValueError('raw_data parameter must be provided')
        
        cols = [y, datetime_col]

        for col in cols:
            #validate if the type is the correct one
            if not isinstance(col, str):
                raise ValueError(f'Column {col} must be provided as str object')
            #validate if column exists
            if col not in raw_data.columns:
                raise ValueError(f'Column name {col} not in index')
        
        try:
            #set a copy to avoid modifying original one
            df_temp = raw_data.copy()
            #set correct dt format and as index
            df_temp.index = pd.to_datetime(df_temp[datetime_col], errors='coerce')
            #delete not a time values
            df_temp = df_temp[df_temp.index.notna()]
            #sort to correct resampling
            df_temp = df_temp.sort_index()

            data_agg = df_temp[y].resample('D').sum()

            return data_agg
        
        except Exception as e:
            raise ValueError(f'Error while creating Serie: {e}')
        
    def prepare_data(self, *,
                     data: pd.DataFrame = None,
                     include_routes: list = [],
                     exclude_routes: list = [],
                     route_col_name: str = 'route_id',
                     ) -> pd.DataFrame:
        
        """
        Filter a DataFrame based on inclusion and exclusion lists of routes.

        This method validates that there are no overlapping routes between the 
        inclusion and exclusion lists, and then filters the rows of the 
        provided DataFrame based on the specified route column.

        Parameters
        ----------
        data : pd.DataFrame, optional
            The input DataFrame containing route information. Must be provided 
            explicitly, by default None.
        include_routes : list, optional
            A list of route IDs to keep in the DataFrame. If empty, all routes 
            are included by default, by default [].
        exclude_routes : list, optional
            A list of route IDs to drop from the DataFrame, by default [].
        route_col_name : str, optional
            The name of the column in `data` that contains the route IDs, 
            by default 'route_id'.

        Returns
        -------
        pd.DataFrame
            A new DataFrame filtered according to the inclusion and 
            exclusion criteria.

        Raises
        ------
        ValueError
            If `data` is not provided (None).
            If `route_col_name` is not present in the columns of `data`.
            If there is any intersection between `include_routes` and 
            `exclude_routes`.

        Examples
        --------
        >>> import pandas as pd
        >>> df = pd.DataFrame({'route_id': [1, 2, 3, 4], 'value': [10, 20, 30, 40]})
        >>> processor.prepare_data(data=df, include_routes=[1, 2, 3], exclude_routes=[3])
           route_id  value
        0         1     10
        1         2     20
        """
        
        if data is None:
            raise ValueError('data parameters must be provided')
        
        if route_col_name not in data.columns:
            raise ValueError('route column name not in index')
        
        df_filtered = data.copy()

        #verify that there is no conflict in both include and exclude list
        conflict = set(include_routes) & set(exclude_routes)
        if conflict:
            raise ValueError(f"Conflict detected: Routes {list(conflict)} cannot be included and excluded simultaneously.")
        
        if include_routes:
            df_filtered = df_filtered[df_filtered[route_col_name].isin(include_routes)]

        if exclude_routes:
            df_filtered = df_filtered[~df_filtered[route_col_name].isin(exclude_routes)]


        return df_filtered

    def _handle_set_nan(self, series: pd.Series, mask: pd.Series) -> pd.Series:
        """
        Replace detected outliers with NaN values.

        This is a private helper method that masks out unwanted anomalies 
        by turning them into ``np.nan``, preserving the original index 
        and length of the series.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be filtered.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A copy of the original series with outliers replaced by ``np.nan``.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, 500.0, 12.0])
        >>> m = pd.Series([False, True, False])
        >>> processor._handle_set_nan(s, m)
        0    10.0
        1     NaN
        2    12.0
        dtype: float64
        """
        s_cleaned = series.copy()
        s_cleaned[mask] = np.nan
        return s_cleaned

    def _handle_drop(self, series: pd.Series, mask: pd.Series) -> pd.Series:
        """
        Drop rows containing outliers entirely from the series.

        This is a private helper method that filters out anomalies using 
        the inverted boolean mask, resulting in a shortened series with 
        the outlier indices completely removed.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be filtered.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A new pandas Series containing only the non-outlier rows, 
            with a reduced length.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> s = pd.Series([10.0, 500.0, 12.0], index=['a', 'b', 'c'])
        >>> m = pd.Series([False, True, False], index=['a', 'b', 'c'])
        >>> processor._handle_drop(s, m)
        a    10.0
        c    12.0
        dtype: float64
        """
        return series[~mask].copy()

    def _handle_linear(self, series: pd.Series, mask: pd.Series) -> pd.Series:
        """
        Impute outliers using linear interpolation between neighboring values.

        This is a private helper method that first replaces detected outliers 
        with ``np.nan`` and then estimates those missing values by drawing a 
        straight line between the remaining valid adjacent data points.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be interpolated.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A copy of the original series with outliers replaced by linearly 
            interpolated values.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, 999.0, 30.0])
        >>> m = pd.Series([False, True, False])
        >>> processor._handle_linear(s, m)
        0    10.0
        1    20.0
        2    30.0
        dtype: float64
        """
        s_cleaned = series.copy()
        s_cleaned = pd.to_numeric(s_cleaned, errors='coerce')
        s_cleaned[mask] = np.nan
        return s_cleaned.interpolate(method='linear')

    def _handle_neighbor_average(
            self, series: pd.Series, mask: pd.Series
        ) -> pd.Series:
        """
        Impute outliers using the average of immediately adjacent neighbors.

        This is a private helper method that replaces outliers with the mean of 
        the previous (t-1) and next (t+1) values. If adjacent neighbors are 
        also outliers, it dynamically falls back to the nearest available 
        valid observations using forward and backward fills.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be smoothed.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A copy of the original series with outliers replaced by the local 
            neighborhood averages.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, 999.0, 20.0])
        >>> m = pd.Series([False, True, False])
        >>> processor._handle_neighbor_average(s, m)
        0    10.0
        1    15.0
        2    20.0
        dtype: float64
        """
        s_cleaned = series.copy()
        s_cleaned[mask] = np.nan

        prev_val = s_cleaned.shift(1)
        next_val = s_cleaned.shift(-1)
        neighbors_mean = (prev_val + next_val) / 2

        fallback_mean = (s_cleaned.ffill() + s_cleaned.bfill()) / 2

        final_mean = neighbors_mean.fillna(fallback_mean)

        return s_cleaned.fillna(final_mean)

    def _handle_zero(self, series: pd.Series, mask: pd.Series) -> pd.Series:
        """
        Replace detected outliers with a constant value of zero.

        This is a private helper method that forces all identified anomalies 
        to ``0.0``, which is useful when outliers represent system errors 
        or invalid spikes that logically imply an absence of activity.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be modified.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A copy of the original series with outliers replaced by ``0.0``.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, -999.0, 12.0])
        >>> m = pd.Series([False, True, False])
        >>> processor._handle_zero(s, m)
        0    10.0
        1     0.0
        2    12.0
        dtype: float64
        """
        s_cleaned = series.copy()
        s_cleaned[mask] = 0.0
        return s_cleaned
    
    def _handle_ffill(self, series: pd.Series, mask: pd.Series) -> pd.Series:
        """
        Impute outliers by propagating the last valid observation forward.

        This is a private helper method that replaces outliers with ``np.nan`` 
        and then uses a Forward Fill (LOCF - Last Observation Carried Forward) 
        strategy to copy the most recent valid historical value into the anomaly 
        slots.

        Parameters
        ----------
        series : pd.Series
            The original pandas Series containing the data to be filled.
        mask : pd.Series
            A boolean pandas Series acting as a mask, where ``True`` indicates 
            that the corresponding element in `series` is an outlier.

        Returns
        -------
        pd.Series
            A copy of the original series with outliers replaced by the 
            preceding valid historical observations.

        See Also
        --------
        delete_outliers_method : The public entry point for outlier handling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, 999.0, 999.0, 15.0])
        >>> m = pd.Series([False, True, True, False])
        >>> processor._handle_ffill(s, m)
        0    10.0
        1    10.0
        2    10.0
        3    15.0
        dtype: float64
        """
        s_cleaned = series.copy()
        s_cleaned[mask] = np.nan
        return s_cleaned.ffill()

    def delete_outliers_method(
            self,
            *,
            series: pd.Series = None,
            outlier_mask: pd.Series = None,
            method: Literal[
                'set_nan', 'drop', 'linear', 'neighbor_average', 'zero', 'ffill'
            ] = 'set_nan',
        ) -> pd.Series:
        """
        Handle detected outliers in a series using a selected strategy.

        This method acts as a central dispatcher that validates input data structures 
        and routes the outlier handling process to specific private helper methods 
        based on the chosen strategy.

        Parameters
        ----------
        series : pd.Series, optional
            The input pandas Series containing anomalies/outliers to be processed. 
            Must be provided explicitly, by default None.
        outlier_mask : pd.Series, optional
            A boolean pandas Series matching the index of `series`, where ``True`` 
            indicates the row is an outlier. Must be provided explicitly, 
            by default None.
        method : {'set_nan', 'drop', 'linear', 'neighbor_average', 'zero', 'ffill'}, optional
            The strategy used to handle or impute the detected outliers:

            * 'set_nan' : Replaces outliers with ``np.nan``, preserving length.
            * 'drop' : Removs outlier rows entirely, reducing series length.
            * 'linear' : Imputes outliers via linear interpolation between neighbors.
            * 'neighbor_average' : Replaces outliers with the local mean of (t-1) and (t+1).
            * 'zero' : Forces outlier values to ``0.0``.
            * 'ffill' : Forward fills using the last known valid historical value.

            By default 'set_nan'.

        Returns
        -------
        pd.Series
            A new pandas Series with the outliers processed according to the 
            selected method.

        Raises
        ------
        ValueError
            If `series` or `outlier_mask` are None or are not instances of ``pd.Series``.
            If the provided `method` string is not found in the valid dispatch options.

        See Also
        --------
        _handle_set_nan : Specific logic for NaN replacement.
        _handle_drop : Specific logic for row removal.
        _handle_linear : Specific logic for linear interpolation.
        _handle_neighbor_average : Specific logic for adjacent neighborhood mean.
        _handle_zero : Specific logic for zero imputation.
        _handle_ffill : Specific logic for forward filling.

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> s = pd.Series([10.0, 999.0, 30.0])
        >>> mask = pd.Series([False, True, False])
        >>> processor.delete_outliers_method(series=s, outlier_mask=mask, method='linear')
        0    10.0
        1    20.0
        2    30.0
        dtype: float64
        """
        if series is None or not isinstance(series, pd.Series):
            raise ValueError(
                f"series parameter must be provided as pd.Series object, you got '{type(series).__name__}' instead"
            )

        if outlier_mask is None or not isinstance(outlier_mask, pd.Series):
            raise ValueError(
                "An outlier_mask (boolean pandas Series) must be provided to identify the outliers."
            )

        dispatch_table = {
            'set_nan': self._handle_set_nan,
            'drop': self._handle_drop,
            'linear': self._handle_linear,
            'neighbor_average': self._handle_neighbor_average,
            'zero': self._handle_zero,
            'ffill': self._handle_ffill,
        }

        handler = dispatch_table.get(method)
        if handler is None:
            raise ValueError(
                f"Invalid method. Expected one of {list(dispatch_table.keys())}, got '{method}'"
            )

        return handler(series, outlier_mask)

        

    


        

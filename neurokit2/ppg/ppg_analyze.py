# -*- coding: utf-8 -*-
import pandas as pd

from .ppg_eventrelated import ppg_eventrelated
from .ppg_intervalrelated import ppg_intervalrelated


def ppg_analyze(data, sampling_rate=1000, method="auto"):
    """**Photoplethysmography (PPG) Analysis**.

    Performs PPG analysis on either epochs (event-related analysis) or on longer periods of data
    such as resting-state data.

    Parameters
    ----------
    data : Union[dict, pd.DataFrame]
        A dictionary of epochs, containing one DataFrame per epoch, usually obtained via
        :func:`.epochs_create`, or a DataFrame containing all epochs, usually obtained via
        :func:`.epochs_to_df`. Can also take a DataFrame of processed signals from a longer period
        of data, typically generated by :func:`.ppg_process` or :func:`.bio_process`. Can also
        take a dict containing sets of separate periods of data.
    sampling_rate : int
        The sampling frequency of the signal (in Hz, i.e., samples/second).
        Defaults to 1000Hz.
    method : str
        Can be one of ``"event-related"`` for event-related analysis on epochs, or
        ``"interval-related"`` for analysis on longer periods of data. Defaults to ``"auto"`` where
        the right method will be chosen based on the mean duration of the data (``"event-related"``
        for duration under 10s).

    Returns
    -------
    DataFrame
        A dataframe containing the analyzed PPG features. If event-related analysis is conducted,
        each epoch is indicated by the ``Label`` column. See :func:`.ppg_eventrelated` and
        :func:`.ppg_intervalrelated` docstrings for details.

    See Also
    --------
    bio_process, ppg_process, epochs_create, ppg_eventrelated, ppg_intervalrelated

    Examples
    ----------
    .. ipython:: python

      import neurokit2 as nk

      # Example 1: Simulate data for event-related analysis
      ppg = nk.ppg_simulate(duration=20, sampling_rate=1000)

      # Process data
      ppg_signals, info = nk.ppg_process(ppg, sampling_rate=1000)
      epochs = nk.epochs_create(ppg_signals, events=[5000, 10000, 15000],
                               epochs_start=-0.1, epochs_end=1.9)

      # Analyze
      analyze_epochs = nk.ppg_analyze(epochs, sampling_rate=1000)
      analyze_epochs


      # Example 2: Download the resting-state data
      data = nk.data("bio_resting_5min_100hz")

      # Process the data
      df, info = nk.ppg_process(data["PPG"], sampling_rate=100)

      # Analyze
      analyze_df = nk.ppg_analyze(df, sampling_rate=100)
      analyze_df

    """
    method = method.lower()

    # Event-related analysis
    if method in ["event-related", "event", "epoch"]:
        # Sanity checks
        if isinstance(data, dict):
            for i in data:
                colnames = data[i].columns.values
        elif isinstance(data, pd.DataFrame):
            colnames = data.columns.values

        if len([i for i in colnames if "Label" in i]) == 0:
            raise ValueError(
                "NeuroKit error: ppg_analyze(): Wrong input or method,"
                "we couldn't extract epochs features."
            )
        else:
            features = ppg_eventrelated(data)

    # Interval-related analysis
    elif method in ["interval-related", "interval", "resting-state"]:
        features = ppg_intervalrelated(data, sampling_rate=sampling_rate)

    # Auto
    elif method in ["auto"]:

        if isinstance(data, dict):
            for i in data:
                duration = len(data[i]) / sampling_rate
            if duration >= 10:
                features = ppg_intervalrelated(data, sampling_rate=sampling_rate)
            else:
                features = ppg_eventrelated(data)

        if isinstance(data, pd.DataFrame):
            if "Label" in data.columns:
                epoch_len = data["Label"].value_counts()[0]
                duration = epoch_len / sampling_rate
            else:
                duration = len(data) / sampling_rate
            if duration >= 10:
                features = ppg_intervalrelated(data, sampling_rate=sampling_rate)
            else:
                features = ppg_eventrelated(data)

    return features
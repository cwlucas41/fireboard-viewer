import requests
import json
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime

deviceName = 'Andúril'


def getCredentials():
    return json.load(sys.stdin)


def login(credentials):
    tokenResponse = requests.post('https://fireboard.io/api/rest-auth/login/',
                                  json=credentials)
    tokenResponse.raise_for_status()
    return {'Authorization': f"Token {tokenResponse.json()['key']}"}


def getDevices(authHeaders):
    devicesResponse = requests.get('https://fireboard.io/api/v1/devices.json',
                                   headers=authHeaders)
    devicesResponse.raise_for_status()
    return devicesResponse.json()


def getSessions(authHeaders):
    sessionsResponse = requests.get('https://fireboard.io/api/v1/sessions.json',
                                    headers=authHeaders)
    sessionsResponse.raise_for_status()
    return sessionsResponse.json()


def getSession(id, authHeaders):
    sessionResponse = requests.get(f"https://fireboard.io/api/v1/sessions/{id}.json",
                                   headers=authHeaders)
    sessionResponse.raise_for_status()
    return sessionResponse.json()


def getChart(id, authHeaders):
    chartResponse = requests.get(f"https://fireboard.io/api/v1/sessions/{id}/chart.json",
                                 headers=authHeaders)
    chartResponse.raise_for_status()
    return chartResponse.json()


def main():
    credentials = getCredentials()
    authHeaders = login(credentials)

    orderedSessions = sorted(getSessions(
        authHeaders), key=lambda session: session['created'], reverse=True)

    lastChart = getChart(orderedSessions[0]['id'], authHeaders)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(hovermode='x')
    for channel in lastChart:
        x = [datetime.datetime.fromtimestamp(x) for x in channel['x']]
        y = channel['y']
        name = channel['label']
        fig.add_trace(go.Scatter(x=x, y=y, name=name))

        dydt_name = f'dy/dt {name}'
        smooth_dydt = np.convolve(np.gradient(y), [1,2,4,2,1])
        fig.add_trace(go.Scatter(x=x, y=smooth_dydt, name=dydt_name, visible='legendonly'), secondary_y=True)

    fig.show()


if __name__ == "__main__":
    main()

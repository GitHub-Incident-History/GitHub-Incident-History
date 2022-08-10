import requests
import json


def download_all_incident_codes():
    incident_codes = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    for page in range(1, 52):
        response = requests.get(
            'https://www.githubstatus.com/history?page=1', headers=headers)
        months = response.json()['months']
        for month in months:
            incidents = month['incidents']
            for incident in incidents:
                # {
                #     'code': '8tnqgcg1qkk1',
                #     'name': 'Incident with Actions, API Requests, Pages and Pull Requests', 
                #     'message': 'This incident has been resolved.',
                #     'impact': 'minor', 'timestamp': "Aug <var data-var='date'>10</var>, <var data-var='time'>00:17</var> - <var data-var='time'>01:30</var> UTC"
                # }
                incident_codes.append(incident['code'])
    with open('incident_codes.json', 'w') as file:
        json.dump(incident_codes, file)


def read_incident_codes():
    incident_codes = []
    with open('incident_codes.json', 'r') as file:
        incident_codes = json.load(file)
    return incident_codes


def main():
    download_all_incident_codes()

    # https://www.githubstatus.com/api/v2/incidents/fjrlf0wn8vmq.json


if __name__ == '__main__':
    main()

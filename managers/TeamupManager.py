import requests
import time

class TeamupManager:
    _databaseManager = None
    _token = None
    _base = "https://api.teamup.com"
    _headers = None

    def __init__(self, bot, teamup_dev_token):
        self._databaseManager = bot._databaseManager
        self._token = teamup_dev_token

        # Check token access
        url = self._base + "/check-access"
        headers = {'Teamup-Token': self._token}
        start_time = time.time()
        r = requests.head(url, headers=headers, timeout=5)
        if r.status_code == 200:
            self._headers = headers
            print("✓ TeamupManager initialized")
            print("  ✓ TeamUP took %s seconds to respond" % (time.time() - start_time))
        else:
            raise Exception("Invalid TeamUP token, use https://apidocs.teamup.com/ a reference OR problem with TeamUP API")
    
    def get_calendar_config(self, calendar_key):
        url = self._base + "/{0}/configuration".format(calendar_key)
        r = requests.get(url, headers=self._headers)
        return {
            'status_code': r.status_code,
            'data': r.json()
        }
    
    def get_calendar_events(self, calendar_key, start_date, end_date, timezone, filters):
        """
            https://api.teamup.com/ksq5het12ahicg5yyz/events?tz=UTC&startDate=2020-01-01&endDate=2020-12-12
        """
        #print("Start_dt={0}, end_dt={1}".format(start_date, end_date))
        url = self._base + "/{0}/events?tz={1}&startDate={2}&endDate={3}".format(calendar_key, timezone, start_date, end_date)
        #print(url)
        r = requests.get(url, headers=self._headers)
        if r.status_code == 200:
            return r.json()["events"]
        else:
            return None
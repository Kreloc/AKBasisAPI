# Meetings section of the BASIS API

headers = {}
headers["X-Alaska-Legislature-Basis-Version"] = "1.2"
headers["X-Alaska-Legislature-Basis-Query"] = "Meetings"
baseUri = 'http://www.akleg.gov/publicservice/basis/'
# session = "31"
Uri = baseUri + "meetings?session=%s&json=true" % session
content = requests.get(Uri, headers=headers)
meetings = json.loads(content.text)

# class Sponsor(object):
#     def __init__(self, Type, Text)


class Meetings(object):
    def __init__(self, Location, Chamber, Title, Schedule, Sponsor):
        self.Location = Location
        self.Chamber = Chamber
        self.Title = Title
        self.Schedule = Schedule
        self.Sponsor = Sponsor

meetingList = list()
for meeting in meetings['Basis']['Meetings']['Meeting']:
    location = ""
    schedule = ""
    sponsor = {}
    title = ""
    if meeting['Location'] != None:
        location = meeting['Location']
    if meeting['Schedule'] != None:
        schedule = meeting['Schedule']
    if meeting['Sponsor'] != None:
        sponsor = meeting['Sponsor']
    if meeting['Title'] != None:
        title = meeting['Title']
    meetingObj = Meetings(location, meeting['chamber'], title, schedule, sponsor)
    meetingList.append(meetingObj)

def getMeetingsToday(session, date = ""):
    
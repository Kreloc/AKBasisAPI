import requests
import json

comList = list()
class CommitteeInfo(object):
    def __init__(self, Name, Code, MeetingDays, Chamber, Category, Members = list()):
        self.Name = Name
        self.Code = Code
        self.MeetingDays = MeetingDays
        self.Chamber = Chamber
        self.Category = Category
        self.Members = Members

def getCommittees(session = "31"):
    headers = {}
    headers["X-Alaska-Legislature-Basis-Version"] = "1.4"
    headers["X-Alaska-Legislature-Basis-Query"] = "Committees,Members"
    Uri = baseUri + "committees?session=%s&json=true" % session
    content = requests.get(Uri, headers=headers)
    coms = json.loads(content.text)
    for com in coms['Basis']['Committees']['Committee']:
        memberList = list()
        if com['CommitteeMembers'] != None:
            for member in com['CommitteeMembers']['MemberDetails']:
                memberList.append(member['EMail'])
        comInfo = CommitteeInfo(com['@name'],com['@code'],com['@MeetingDays'],com['@chamber'],com['@category'],memberList)
        comList.append(comInfo)
    return comList
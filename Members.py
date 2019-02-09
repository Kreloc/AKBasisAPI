
import requests
import json

class MemberInfo(object):
    def __init__(self, FirstName, MiddleName, LastName, Name, Email, Phone, District, Party, Building, Room, Chamber, Code, PhotoUrl):
        self.FirstName = FirstName
        self.MiddleName = MiddleName
        self.LastName = LastName
        self.Name = Name
        self.Email = Email
        self.Phone = Phone
        self.District = District
        self.Party = Party
        self.Building = Building
        self.Room = Room
        self.Chamber = Chamber
        self.Code = Code
        self.PhotoUrl = PhotoUrl

# http://akleg.gov/images/legislators/rounded/CAE.png
# Interim contact info is not available from the API. Fax numbers are also not available from the API
# openstates complies the following info for people.py - (Session Contact: Address at Capitol; PhoneNumber; Fax); Email; (InterimContact: Address for District Office, Phone, Fax);
# primary_org=Chamber,district,name,party(As a word not the letter), image, 
# 'R' : "Republican",'D' : 'Democractic', 'N' : 'Independent'

def getMembers(session = "31"):
    headers = {}
    headers["X-Alaska-Legislature-Basis-Version"] = "1.4"
    headers["X-Alaska-Legislature-Basis-Query"] = "Members"
    baseUri = 'http://www.akleg.gov/publicservice/basis/'
    # session = "31"
    Uri = baseUri + "members?session=%s&json=true" % session
    content = requests.get(Uri, headers=headers)
    memberList = list()
    if content.ok == True:
        members = json.loads(content.text)
        for member in members['Basis']['Members']['Member']:
            details = member['MemberDetails'][0]
            photoUrl = "http://akleg.gov/images/legislators/rounded/%s.png" % details['@code']
            Name = "%s %s" % (details['FirstName'], details['LastName'])
            memberObject = MemberInfo(details['FirstName'],details['MiddleName'],details['LastName'], Name,details['EMail'],details['Phone'],details['District'],details['Party'],details['Building'],details['Room'],details['@chamber'],details['@code'], photoUrl)
            memberList.append(memberObject)
    
    return memberList

import requests
import json
import base64

class BillObject(object):
    def __init__(self, billId, chamber, ShortTitle, fullTextUrl, StatusDate, StatusCode, StatusText, Versions = list()):
        self.billId = billId
        self.chamber = chamber
        self.ShortTitle = ShortTitle
        self.fullTextUrl = fullTextUrl
        self.StatusDate = StatusDate
        self.StatusCode = StatusCode
        self.StatusText = StatusText
        self.Versions = Versions

class BillVersion(object):
    def __init__(self, Title, IntroDate, VersionLetter, Name):
        self.Title = Title
        self.IntroDate = IntroDate
        self.VersionLetter = VersionLetter
        self.Name = Name

# moved this into a function, since this logic is needed in two places...hate repeating code.
def getBillContentFromJson(Uri, headers = {}):
    billList = list()
    content = requests.get(Uri, headers=headers)
    bills = json.loads(content.text)
    for bill in bills['Basis']['Bills']['Bill']:
        versionList = list()
        if bill['Versions'] != None:
            for version in bill['Versions']['Version']:
                versionInfo = BillVersion(version['Title'],version['@introdate'],version['@versionletter'],version['@name'])
                versionList.append(versionInfo)
        # if the bill was withdrawn, it will no longer have the text available, default to the Alaska State Legislature website for url in that case
        textUrl = "http://www.akleg.gov"
        statCode = ""
        statText = ""
        if bill['FullText'] != None:
            textUrl = bill['FullText']['Content'][0]['Url']       
        if bill['StatusText'] != None:
            statCode = bill['StatusText']['@statuscode']
            statText = bill['StatusText']['#text']
        billInfo = BillObject(bill['@billnumber'],bill['@chamber'],bill['ShortTitle'],textUrl,bill['StatusDate'],statCode,statText,versionList)
        if billInfo != None:
            billList.append(billInfo)
    return billList

def getBills(session = "31"):
    billList = list()
    headers = {}
    headers["X-Alaska-Legislature-Basis-Version"] = "1.2"
    headers["X-Alaska-Legislature-Basis-Query"] = "Bills;fulltext=urlonly,Versions"
    baseUri = 'http://www.akleg.gov/publicservice/basis/'
    Uri = baseUri + "bills?session=%s&json=true" % session
    # getting a count back, tends to take a little while
    headContent = requests.head(Uri, headers=headers)
    itemsReturnedCount = int(headContent.headers['X-Alaska-Query-Count'])
    if itemsReturnedCount <= 100:
        billList = getBillContentFromJson(Uri, headers)
    else:
        # change headers to iterate thru using range query qualifier
        howManyLoops = int(itemsReturnedCount / 50) + (itemsReturnedCount % 50 > 0)
        i = 0
        j = 50
        for thatMany in range(howManyLoops):
            headers["X-Alaska-Query-ResultRange"] = "%s..%s" % (i,j)
            print(headers)
            tempBillList = getBillContentFromJson(Uri, headers)
            for billItem in tempBillList:
                billList.append(billItem)
            i = j + 1
            j = i + 50
            if thatMany == howManyLoops - 1:
                j = itemsReturnedCount
    return billList

### Below is work for getting detailed information for a bill
# Sponsors can be a few different ways. Sometimes its a member, sometimes committee, sometimes governor
class Votes(object):
    def __init__(self, MemberCode, Date, Title, Vote):
        self.MemberCode = MemberCode
        self.Date = Date
        self.Title = Title
        self.Vote = Vote

class FiscalNote(object):
    def __init__(self, Chamber, FiscalImpact, Preparer, Name, Date, Url):
        self.Chamber = Chamber
        self.FiscalImpact = FiscalImpact
        self.Preparer = Preparer
        self.Name = Name
        self.Date = Date
        self.Url = Url

class Sponsors(object):
    def __init__(self, Name, Primary, SponsorStatement, Requestor, Committee):
        self.Name = Name
        self.Primary = Primary
        self.SponsorStatement = SponsorStatement
        self.Requestor = Requestor
        self.Committee = Committee

class Actions(object):
    def __init__(self, JournalPage, Chamber, Code, ActionText, JournalDate):
        self.JournalPage = JournalPage
        self.Chamber = Chamber
        self.Code = Code
        self.ActionText = ActionText
        self.JournalDate = JournalDate

class BillVersion(object):
    def __init__(self, Title, IntroDate, VersionLetter, Name):
        self.Title = Title
        self.IntroDate = IntroDate
        self.VersionLetter = VersionLetter
        self.Name = Name

class BillObject(object):
    def __init__(self, billId, chamber, ShortTitle, fullTextUrl, StatusDate, StatusCode, StatusText, Versions, Subjects, Votes, FiscalNote, Sponsors, Actions, BillText):
        self.billId = billId
        self.chamber = chamber
        self.ShortTitle = ShortTitle
        self.fullTextUrl = fullTextUrl
        self.StatusDate = StatusDate
        self.StatusCode = StatusCode
        self.StatusText = StatusText
        self.Versions = Versions
        self.Subjects = Subjects
        self.Votes = Votes
        self.FiscalNote = FiscalNote
        self.Sponsors = Sponsors
        self.Actions = Actions
        self.BillText = BillText




def getBillDetailed(billId,session = "31", fullText = False):
    print("Going to get full details on entered bill")
    # Only set fullText to true if you want the full plain text of the bill
    # Subjects as list
    # Votes as list
    # Cannot use Verions and Actions in the same query...ask Shay if this behavior is intended?
    # Make second query to only get Versions info for now
    # Fulltext is encoding in base64. Use base64 module. Fulltext has certain special characters for text decorating.
    # 'b denotes beginning of text; \x16..\x17 = Bold; \x10..\x11 = Underline where .. is the text in between those characters
    #headers["X-Alaska-Legislature-Basis-Query"] = "Bills;bill=sb 105,actions,fulltext,Sponsors,Subjects,Fiscalnotes,Votes"
    headers = {}
    headers["X-Alaska-Legislature-Basis-Version"] = "1.2"
    if fullText == True:
        headers["X-Alaska-Legislature-Basis-Query"] = "Bills;bill=%s;fulltext,actions,fulltext,Sponsors,Subjects,Fiscalnotes,Votes" % billId
    else:
        headers["X-Alaska-Legislature-Basis-Query"] = "Bills;bill=%s;fulltext=urlonly,actions,fulltext,Sponsors,Subjects,Fiscalnotes,Votes" % billId
    baseUri = 'http://www.akleg.gov/publicservice/basis/'
    Uri = baseUri + "bills?session=%s&json=true" % session
    content = requests.get(Uri, headers=headers)
    bills = json.loads(content.text)
    rtrnBillList = list()
    for bill in bills['Basis']['Bills']['Bill']:
        actionList = list()
        VoteRecord = list()
        fiscalNotes = list()
        sponsorList = list()
        subjectList = list()
        versionList = list()
        billText = ""
        if bill['Actions'] != None:
            for actionItem in bill['Actions']['Action']:
                newActionObj = Actions(actionItem['@journalpage'],actionItem['@chamber'],actionItem['@code'],actionItem['ActionText'],actionItem['@journaldate'])
                actionList.append(newActionObj)
        if bill['Votes'] != None:
            for voteItem in bill['Votes']['Vote']:
                newVoteObj = Votes(voteItem['Member'], voteItem['Date'],voteItem['Title'],voteItem['@vote'])
                VoteRecord.append(newVoteObj)
        if bill['FiscalNotes'] != None:
            for fiscalItem in bill['FiscalNotes']['FiscalNote']:
                newFiscalObj = FiscalNote(fiscalItem['@chamber'],fiscalItem['@fiscalimpact'],fiscalItem['@preparer'],fiscalItem['@name'],fiscalItem['@date'],fiscalItem['Content']['Url'])
                fiscalNotes.append(newFiscalObj)
        statement = ""
        SponsorName = ""
        requestor = ""
        SponsorCommittee = ""
        billUrl = ""
        if bill['Sponsors']['SponsorStatement'] != None:
            statement = sponsorItem['SponsorStatement']
        if bill['Sponsors'].get('Requestor') != None:
            requestor = bill['Sponsors']['Requestor']
            newSponsorObj = Sponsors("",False, statement, requestor)
            sponsorList.append(newSponsorObj)
        if bill['Sponsors'].get('MemberDetails') != None:
            for member in bill['Sponsors']['MemberDetails']:
                Primary = False
                SponsorName = member['EMail']
                if member.get('@primesponsor') == 'true':
                    Primary = True
                newSponsorObj = Sponsors(SponsorName, Primary, statement, requestor, SponsorCommittee)
                sponsorList.append(newSponsorObj)
        if bill['FullText']['Content'] != None:
            if fullText == True:
                billText = base64.b64decode(bill['FullText']['Content'][0]['Bytes']['#text'])
            textUrl = bill['FullText']['Content'][0]['Url']
        subjectList = bill['Subjects']['Subject']
        statCode = ""
        statText = ""
        if bill['StatusText'] != None:
            statCode = bill['StatusText']['@statuscode']
            statText = bill['StatusText']['#text']
        billObj = BillObject(bill['@billnumber'],bill['@chamber'],bill['ShortTitle'],textUrl,bill['StatusDate'],statCode, statText, versionList, subjectList, VoteRecord, fiscalNotes, sponsorList, actionList, billText)
        rtrnBillList.append(billObj)
    return rtrnBillList




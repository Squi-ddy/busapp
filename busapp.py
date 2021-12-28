import re, threading, requests, copy, datetime, loadingbar
from functools import partial
from tkinter import *

class App(object):

    def __init__(self):
        self.root = Tk()
        self.root.title("Search Bus Stops!")
        self.root.geometry(str(self.root.winfo_screenwidth()-50)+'x'+ str(self.root.winfo_screenheight()-50)+'+15+5') 
        self.root.resizable(0,0)
        self.acckey = 'whw5SgO8Td68IN2BXBU3tA=='
        self.busstops = []
        self.busstoprds = []
        self.busstopcodes = []
        self.stopdispname = []
        self.findstopcodequick = {}
        self.finddescquick = {}
        self.finddispnamequick = {}
        self.lastinput = ''
        self.resultslist = []
        self.bustimes = []
        self.shownrange = 0
        self.bustimesshownrange = 0
        self.loading = False
        self.root.reloadimg = PhotoImage(file = 'assets/reload.gif')
        self.root.search = PhotoImage(file = 'assets/search.gif')
        t = threading.Timer(0, self.loadbusstops)
        t.daemon = True
        t.start()
        self.loadsearch()
        self.root.mainloop()

    def titlecase(self, s):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",lambda mo: mo.group(0)[0].upper()+mo.group(0)[1:].lower(),s)

    def expandcommonabbr(self, s):
        subs = [(' ter', ' terminal'),
        ('Aye', 'AYE'),
        ('Rd', 'Road'),
        ('Lor ', 'Lorong '),
        ('Jln', 'Jalan'),
        (r'St\.', 'Saint'),
        (' St ', ' Street '),
        (' St$', ' Street'),
        ('Ctrl', 'Central'),
        ('Cres', 'Crescent'),
        ('Ave', 'Avenue'),
        ('Bt', 'Bukit'),
        ('Macpherson', 'MacPherson'),
        ('Dr', 'Drive'),
        ('Sg', 'Sungei'),
        ('Nth', 'North'),
        ('Sth', 'South'),
        ('Upp', 'Upper'),
        ('S\'goon', 'Serangoon'),
        ('Ctr', 'Center'),
        ('Sq', 'Square'),
        ('Pk', 'Park'),
        ('Mcnair', 'McNair'),
        ('C\'wealth', 'Commonwealth'),
        ('Terr', 'Terrence'),
        ('Gr', 'Grove'),
        ('aft', 'after'),
        ('bef', 'before'),
        (' est', ' estate'),
        ('cplx', 'complex'),
        ('comm', 'community'),
        ('hq', 'headquarters'),
        ('blk', 'block'),
        ('opp', 'opposite'),
        ('ctr', 'center'),
        ('bldg', 'building'),
        ('sch', 'school'),
        ('stn', 'station'),
        ('hse', 'house'),
        ('pk', 'park'),
        (' st ', ' street '),
        ('co ', 'company'),
        ('tp', 'temple'),
        ('pte', 'private'),
        ('ltd', 'limited'),
        ('twr', 'tower'),
        ('nth', 'north'),
        ('engrg', 'engineering'),
        ("w'lands", 'woodlands'),
        ("checkpt", 'checkpoint'),
        ("pr ", 'primary '),
        ("ind ", 'industrial '),
        ("jc", 'junior college'),
        ("hosp", 'hospital'),
        ('s\'goon', 'serangoon'),
        (' int', ' interchange'),
        ('gdn', 'garden'),
        ('mkt', 'market'),
        ('fc', 'food centre'),
        ('cp$', 'carpark'),
        ('sec', 'secondary'),
        ('mque', 'mosque'),
        (' pt', ' point'),
        ('cc', 'community centre'),
        ('cemy', 'cemetery'),
        (' rd', ' road'),
        ('amk', 'ang mo kio'),
        ('div', 'division'),
        (' ch ', ' church '),
        (' ch$', ' church'),
        ('gr', 'grove'),
        ('hts', 'heights'),
        ('bt', 'bukit'),
        ('c\'wealth', 'commonwealth')]
        for i, j in subs:
            s = re.sub(i, j, s)
        return s

    def loadbusstops(self, skipamt = 0):
        data = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusStops', headers = {'AccountKey': self.acckey, 'accept': 'application/json'}, params = {'$skip': str(skipamt)})
        data = data.json()
        if len(data['value']) > 0:
            inf = []
            for stop in data['value']:
                self.busstops.append(stop['Description'].upper())
                self.busstoprds.append(self.expandcommonabbr(self.titlecase(stop['RoadName'])))
                self.busstopcodes.append(stop['BusStopCode'])
                self.finddescquick[stop['BusStopCode']] = stop['Description'].upper()+ '//' +self.expandcommonabbr(self.titlecase(stop['RoadName']))
                self.findstopcodequick[stop['Description'].upper()+ '//' +self.expandcommonabbr(self.titlecase(stop['RoadName']))] = stop['BusStopCode']
                self.finddispnamequick[stop['BusStopCode']] = self.expandcommonabbr(stop['Description'].lower()).upper()
                self.stopdispname.append(self.expandcommonabbr(stop['Description'].lower()).upper())
            self.loadbusstops(skipamt + 500)
        else:
            return

    def getresults(self):
        if not self.loading:
            t = threading.Thread(target = self.updateresults)
            t.daemon = True
            t.start()
            self.loading = True
            self.loadingbar.start()

    def loadsearch(self):
        self.searchboxframe = Frame(self.root, bd = 1, relief = SOLID, highlightthickness = 0, width = (self.root.winfo_screenwidth()-50)//2+50, height = (self.root.winfo_screenwidth()-50)//20, background = 'white')
        self.searchboxframe.place(relx = .5, rely = .15, anchor = CENTER)
        self.loadingcanvas = Canvas(self.root, bg = self.root["bg"], width = (self.root.winfo_screenwidth()-50)//2+50, height = (self.root.winfo_screenwidth()-50)//60)
        self.loadingcanvas.place(relx = .5, rely = .215, anchor = CENTER)
        self.loadingbar = loadingbar.loading(self.root, self.loadingcanvas, 3)
        self.searchbox = Entry(self.searchboxframe, bd = 0, highlightthickness = 0, font = ('Arial Narrow', '40'))
        self.searchbox.place(relx = .5, x = -35, rely = .5, anchor = CENTER, relheight = .9, relwidth = .96, width = -70)
        self.searchbutton = Button(self.searchboxframe, bd = 0, highlightthickness = 0, image = self.root.search, bg = '#FFFFFF', activebackground = '#FFFFFF', relief = SUNKEN, command = self.getresults)
        self.searchbutton.place(relx = .99, x = -56, rely = .5, y = -1, anchor = W, relheight = .9, width = 55)
        self.resultsframe = Frame(self.root, bd = .5, relief = SOLID, highlightthickness = 0, width = (self.root.winfo_screenwidth()-50)//2+50, height = (self.root.winfo_screenwidth()-50)//2.5, bg = 'gray85')
        self.resultsframe.place(relx = .5, rely = .6, anchor = CENTER)
        

    def updateresults(self):
        try:
            int(self.searchbox.get())
            isInt = True
        except ValueError:
            isInt = False
        if self.lastinput != self.searchbox.get() and ((len(self.searchbox.get()) > 2 and isInt == False) or (len(self.searchbox.get()) >= 1 and isInt == True)):
            self.lastinput = self.searchbox.get()
            notCode = False
            try:
                int(self.lastinput)
            except:
                notCode = True
            if notCode:
                searchresultlist, whichones = self.simpleSearch(self.busstops, self.lastinput, special = self.stopdispname)
            else:
                searchresultlist, whichones = self.simpleSearch(self.busstopcodes, self.lastinput)
            for x in self.resultslist:
                x.destroy()
            if len(searchresultlist) > 0:
                resultsplaced = 0
                dif = 0
                alreadyplaced = []
                self.shown = '1-5'
                pagelabel = Label(self.resultsframe, font = ("Arial Narrow", '10'), text = 'Page 1', bg = 'gray85', highlightthickness = 0, bd = 0)
                pagelabel.place(relx = .5, rely = .94, anchor = CENTER, relheight = .03, relwidth = .5)
                self.resultslist.append(pagelabel)
                for x in searchresultlist:
                    if (resultsplaced - dif) < 5:
                        stopall = False
                        try:
                            int(x)
                            desc = self.finddescquick[x]
                            r = re.match('.+//', desc)
                            stopname = r.group()[:-2]
                            r = re.search('//.+', desc)
                            stoprd = r.group()[2:]
                            stopcode = x
                            stopdispname = self.finddispnamequick[stopcode]
                            alreadyplaced.append(x)
                        except:
                            if self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]] in alreadyplaced:
                                stopall = True
                                dif += 1
                            else:
                                stopcode = self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]]
                                stopname = x
                                stoprd = self.busstoprds[whichones[resultsplaced]]
                                alreadyplaced.append(stopcode)
                                stopdispname = self.finddispnamequick[stopcode]
                        if stopall == False:
                            result = Frame(self.resultsframe, bd = 1, relief = SOLID, highlightthickness = 0, bg = 'white')
                            result.bind('<Button-1>', partial(self.preshowtime, stopcode))
                            result.place(relx = .5, rely = .1 + .18 * (resultsplaced - dif), anchor = CENTER, relwidth = .95, relheight = .17)
                            resulttext = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stopdispname, font = ('Arial Narrow', '20', 'bold'))
                            resulttext.bind('<Button-1>', partial(self.preshowtime, stopcode))
                            resulttext.place(relx = .5, rely = .2, anchor = CENTER, relheight = .4, relwidth = .95)
                            resultrd = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stoprd, font = ('Arial Narrow', '15'))
                            resultrd.bind('<Button-1>', partial(self.preshowtime, stopcode))
                            resultrd.place(relx = .5, rely = .5, anchor = CENTER, relheight = .25, relwidth = .95)
                            resultcode = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = '('+stopcode+')', font = ('Arial Narrow', '15'))
                            resultcode.bind('<Button-1>', partial(self.preshowtime, stopcode))
                            resultcode.place(relx = .5, rely = .8, anchor = CENTER, relheight = .22, relwidth = .95)
                            self.resultslist.append(result)
                            self.resultslist.append(resulttext)
                            self.resultslist.append(resultcode)
                        resultsplaced += 1
                    elif (resultsplaced - dif) == 5:
                        nextbutton = Button(self.resultsframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '>', font = ('Arial Narrow', '10'), command = partial(self.shownext, searchresultlist, whichones))
                        nextbutton.place(relx = .5, rely = .96, x = 5, anchor = NW, relheight = .03, relwidth = .03)
                        self.resultslist.append(nextbutton)
                        break
            else:
                result = Label(self.resultsframe, bd = 0, highlightthickness = 0, bg = 'gray85', text = 'No bus stops found.', font = ('Arial Narrow', '30', 'bold'))
                result.place(relx = .5, rely = .5, anchor = CENTER, relwidth = .95, relheight = .5)
                self.resultslist.append(result)
        self.loading = False
        self.loadingbar.stop()

    def shownext(self, searchresultlist, whichones):
        resultsplaced = 0
        dif = 0
        r = re.search('-.+', self.shown)
        stop = int(r.group()[1:]) + 5
        r = re.match('.+-', self.shown)
        start = int(r.group()[:-1]) + 5
        alreadyplaced = []
        for x in self.resultslist:
            x.destroy()
        backbutton = Button(self.resultsframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '<', font = ('Arial Narrow', '10'), command = partial(self.showprev, searchresultlist, whichones))
        backbutton.place(relx = .5, rely = .96, x = -5, anchor = NE, relheight = .03, relwidth = .03)
        self.resultslist.append(backbutton)
        self.shown = str(start)+'-'+str(stop)
        pagelabel = Label(self.resultsframe, font = ("Arial Narrow", '10'), text = 'Page '+str(stop//5), bg = 'gray85', highlightthickness = 0, bd = 0)
        pagelabel.place(relx = .5, rely = .94, anchor = CENTER, relheight = .03, relwidth = .5)
        self.resultslist.append(pagelabel)
        for x in searchresultlist:
            if (resultsplaced - dif) < (start - 1):
                stopall = False
                try:
                    int(x)
                    alreadyplaced.append(x)
                except:
                    if self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]] in alreadyplaced:
                        stopall = True
                        dif += 1
                    else:
                        alreadyplaced.append(self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]])
                resultsplaced += 1
            elif (resultsplaced - dif) < stop:
                stopall = False
                try:
                    int(x)
                    desc = self.finddescquick[x]
                    r = re.match('.+//', desc)
                    stopname = r.group()[:-2]
                    r = re.search('//.+', desc)
                    stoprd = r.group()[2:]
                    stopcode = x
                    stopdispname = self.finddispnamequick[x]
                    alreadyplaced.append(x)
                except:
                    if self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]] in alreadyplaced:
                        stopall = True
                        dif += 1
                    else:
                        stopcode = self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]]
                        stopname = x
                        stoprd = self.busstoprds[whichones[resultsplaced]]
                        alreadyplaced.append(stopcode)
                        stopdispname = self.finddispnamequick[stopcode]
                if stopall == False:
                    result = Frame(self.resultsframe, bd = 1, relief = SOLID, highlightthickness = 0, bg = 'white')
                    result.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    result.place(relx = .5, rely = .1 + .18 * (resultsplaced - start - dif + 1), anchor = CENTER, relwidth = .95, relheight = .17)
                    resulttext = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stopdispname, font = ('Arial Narrow', '20', 'bold'))
                    resulttext.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resulttext.place(relx = .5, rely = .2, anchor = CENTER, relheight = .4, relwidth = .95)
                    resultrd = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stoprd, font = ('Arial Narrow', '15'))
                    resultrd.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resultrd.place(relx = .5, rely = .5, anchor = CENTER, relheight = .25, relwidth = .95)
                    resultcode = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = '('+stopcode+')', font = ('Arial Narrow', '15'))
                    resultcode.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resultcode.place(relx = .5, rely = .8, anchor = CENTER, relheight = .22, relwidth = .95)
                    self.resultslist.append(result)
                    self.resultslist.append(resulttext)
                    self.resultslist.append(resultcode)
                resultsplaced += 1
            elif (resultsplaced - dif) == stop:
                nextbutton = Button(self.resultsframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '>', font = ('Arial Narrow', '10'), command = partial(self.shownext, searchresultlist, whichones))
                nextbutton.place(relx = .5, rely = .96, x = 5, anchor = NW, relheight = .03, relwidth = .03)
                self.resultslist.append(nextbutton)
                break

    def showprev(self, searchresultlist, whichones):
        resultsplaced = 0
        dif = 0
        r = re.search('-.+', self.shown)
        stop = int(r.group()[1:]) - 5
        r = re.match('.+-', self.shown)
        start = int(r.group()[:-1]) - 5
        alreadyplaced = []
        for x in self.resultslist:
            x.destroy()
        nextbutton = Button(self.resultsframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '>', font = ('Arial Narrow', '10'), command = partial(self.shownext, searchresultlist, whichones))
        nextbutton.place(relx = .5, rely = .96, x = 5, anchor = NW, relheight = .03, relwidth = .03)
        self.resultslist.append(nextbutton)
        self.shown = str(start) + '-' + str(stop)
        pagelabel = Label(self.resultsframe, font = ("Arial Narrow", '10'), text = 'Page '+str(stop//5), bg = 'gray85', highlightthickness = 0, bd = 0)
        pagelabel.place(relx = .5, rely = .94, anchor = CENTER, relheight = .03, relwidth = .5)
        self.resultslist.append(pagelabel)
        for x in searchresultlist:
            if (resultsplaced - dif) == 0 and (start-1)>0:
                backbutton = Button(self.resultsframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '<', font = ('Arial Narrow', '10'), command = partial(self.showprev, searchresultlist, whichones))
                backbutton.place(relx = .5, rely = .96, x = -5, anchor = NE, relheight = .03, relwidth = .03)
                self.resultslist.append(backbutton)
            if (resultsplaced - dif) < (start - 1):
                stopall = False
                try:
                    int(x)
                    alreadyplaced.append(x)
                except:
                    if self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]] in alreadyplaced:
                        stopall = True
                        dif += 1
                    else:
                        alreadyplaced.append(self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]])
                resultsplaced += 1
            elif (resultsplaced - dif) < stop:
                stopall = False
                try:
                    int(x)
                    desc = self.finddescquick[x]
                    r = re.match('.+//', desc)
                    stopname = r.group()[:-2]
                    r = re.search('//.+', desc)
                    stoprd = r.group()[2:]
                    stopcode = x
                    stopdispname = finddispnamequick[x]
                    alreadyplaced.append(x)
                except:
                    if self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]] in alreadyplaced:
                        stopall = True
                        dif += 1
                    else:
                        stopcode = self.findstopcodequick[x + '//' + self.busstoprds[whichones[resultsplaced]]]
                        stopname = x
                        stoprd = self.busstoprds[whichones[resultsplaced]]
                        alreadyplaced.append(stopcode)
                        stopdispname = self.finddispnamequick[stopcode]
                if stopall == False:
                    result = Frame(self.resultsframe, bd = 1, relief = SOLID, highlightthickness = 0, bg = 'white')
                    result.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    result.place(relx = .5, rely = .1 + .18 * (resultsplaced - start - dif + 1), anchor = CENTER, relwidth = .95, relheight = .17)
                    resulttext = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stopdispname, font = ('Arial Narrow', '20', 'bold'))
                    resulttext.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resulttext.place(relx = .5, rely = .2, anchor = CENTER, relheight = .4, relwidth = .95)
                    resultrd = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = stoprd, font = ('Arial Narrow', '15'))
                    resultrd.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resultrd.place(relx = .5, rely = .5, anchor = CENTER, relheight = .25, relwidth = .95)
                    resultcode = Label(result, bd = 0, highlightthickness = 0, bg = 'white', text = '('+stopcode+')', font = ('Arial Narrow', '15'))
                    resultcode.bind('<Button-1>', partial(self.preshowtime, stopcode))
                    resultcode.place(relx = .5, rely = .8, anchor = CENTER, relheight = .22, relwidth = .95)
                    self.resultslist.append(result)
                    self.resultslist.append(resulttext)
                    self.resultslist.append(resultcode)
                resultsplaced += 1
            else:
                break

    def btm(self):
        self.stoptimestext.destroy()
        self.bustimesframe.destroy()
        self.backmenubutton.destroy()
        for x in self.bustimes:
            x.destroy()
        self.loadsearch()

    def btmE(self, e):
        self.lastinput = ""
        self.btm()

    def preshowtime(self, stopcode, event):
        self.resultsframe.place_forget()
        self.searchboxframe.place_forget()
        self.searchbox.place_forget()
        for x in self.resultslist:
            x.destroy()
        self.stoptimestext = Label(self.root, font=("Arial Narrow", "20", 'bold'), bd = .5, relief = SOLID, highlightthickness = 0, bg = 'white', text = 'Bus Arrival Times at '+self.finddispnamequick[stopcode])
        self.stoptimestext.place(relx = .5, rely = .1, anchor = CENTER, relwidth = .6, relheight = .07)
        self.bustimesframe = Frame(self.root, bd = .5, relief = SOLID, highlightthickness = 0, bg = 'gray85')
        self.bustimesframe.place(relx = .5, rely = .55, anchor = CENTER, relwidth = .6, relheight = .8)
        self.backmenubutton = Button(self.root, bd = 1, highlightthickness = 0, bg = 'white', text = 'Go Back', font=("Arial Narrow", "20"), relief = SOLID)
        self.backmenubutton.bind("<Button-1>", self.btmE)
        self.backmenubutton.place(relx = .15, rely = .1, x = -1, y = -1, anchor = CENTER, relwidth = .07, relheight = .07)
        self.showbustimes(stopcode, False)

    def showbustimesE(self, stopcode, isNotPre, showrange = 0, e = 0):
        self.showbustimes(stopcode, isNotPre, showrange)

    def showbustimes(self, stopcode, isNotPre, showrange = 0):
        if isNotPre:
            for x in self.bustimes:
                x.destroy()
        data = requests.get('http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2', headers = {'AccountKey': self.acckey, 'accept': 'application/json'}, params = {'BusStopCode': stopcode})
        data = data.json()
        timenow = datetime.datetime.now()
        currmin = timenow.minute
        currhr = timenow.hour
        count = 0
        if showrange == 0:
            stop = 5
            start = 1
        else:
            r = re.search('-.+', showrange)
            stop = int(r.group()[1:])
            r = re.match('.+-', showrange)
            start = int(r.group()[:-1])
        self.bustimes = []
        pagelabel = Label(self.bustimesframe, font = ("Arial Narrow", '10'), text = 'Page '+str(stop//5), bg = 'gray85', highlightthickness = 0, bd = 0)
        pagelabel.place(relx = .5, rely = .94, anchor = CENTER, relheight = .03, relwidth = .5)
        self.bustimes.append(pagelabel)
        reloadbutton = Label(self.bustimesframe, image = self.root.reloadimg, bg = 'white', highlightthickness = 0, bd = 0.5, relief = SOLID)
        reloadbutton.bind('<Button-1>', partial(self.showbustimesE, stopcode, True, str(start)+'-'+str(stop)))
        reloadbutton.place(relx = .03, rely = .96, x = -1, y = -1, anchor = CENTER, relheight = .03, relwidth = .04)
        self.bustimes.append(reloadbutton)
        for x in data['Services']:
            if count < stop and count >= (start-1):
                skip = False
                try:
                    timemin = int(x['NextBus']['EstimatedArrival'][14:16])
                except ValueError:
                    skip = True
                if skip:
                    bus1frame = Frame(bustimeframe, bg = 'steelblue2', bd = 0, highlightthickness = 0)
                    bus1frame.place(relx = .2, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    est = Label(bus1frame, bg = bus1frame['bg'], bd = 0, highlightthickness = 0, font = 'Arial 15', text = 'No Estimate\nAvailable!')
                    est.place(relx = 0.5, rely = 0.5, anchor = CENTER, relwidth = .9, relheight = .9)
                    self.bustimes.append(bus1frame)
                    self.bustimes.append(est)
                else:
                    timehr = int(x['NextBus']['EstimatedArrival'][11:13])
                    if timemin < currmin and timehr > currhr:
                        if timemin + 60 > currmin:
                            arrtime1 = str(timemin + 60 - currmin) + 'm'
                        else:
                            arrtime1 = '>1h'
                    elif timemin < currmin and timehr == currhr:
                        arrtime1 = 'Arr'
                    elif timemin == currmin:
                        arrtime1 = 'Arr'
                    else:
                        arrtime1 = str(timemin - currmin) + 'm'
                    bustimeframe = Frame(self.bustimesframe, bd = 1, relief = SOLID, highlightthickness = 0, bg = 'white')
                    bustimeframe.place(relx = .5, rely = .1 + .18 * (count-start+1), anchor = CENTER, relwidth = .95, relheight = .17)
                    busno = Label(bustimeframe, bg = 'white', bd = 0, highlightthickness = 0, font = ('Arial', '45'), text = ' '+x['ServiceNo'])
                    busno.place(relx = 0, rely = .5, anchor = W)
                    bus1frame = Frame(bustimeframe, bg = 'chartreuse2' if x['NextBus']['Load'] == 'SEA' else 'yellow2' if x['NextBus']['Load'] == 'SDA' else 'red2', bd = 0, highlightthickness = 0)
                    bus1frame.place(relx = .2, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    bus1time = Label(bus1frame, bg = bus1frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '20') if arrtime1 != 'Arr' else ('Arial', '20', 'bold'), text = arrtime1 if arrtime1 == 'Arr' else '~'+arrtime1)
                    bus1time.place(relx = .5, rely = .15, anchor = CENTER, relheight = .2, relwidth = .9)
                    singledoubledeck = Label(bus1frame, bg = bus1frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Double Decker' if x['NextBus']['Type'] == 'DD' else 'Single Decker' if x['NextBus']['Type'] == 'SD' else 'Long and Bendy')
                    singledoubledeck.place(relx = .5, rely = .4, anchor = CENTER, relheight = .25, relwidth = .9)
                    wab = Label(bus1frame, bg = bus1frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Wheelchairs allowed!' if x['NextBus']['Feature'] == 'WAB' else 'No wheelchairs!')
                    wab.place(relx = .5, rely = .7, anchor = CENTER, relheight = .25, relwidth = .9)
                    self.bustimes.append(bustimeframe)
                    self.bustimes.append(busno)
                    self.bustimes.append(bus1time)
                    self.bustimes.append(bus1frame)
                    self.bustimes.append(singledoubledeck)
                    self.bustimes.append(wab)
                skip = False
                try:
                    timemin = int(x['NextBus2']['EstimatedArrival'][14:16])
                except ValueError:
                    skip = True
                if skip:
                    bus2frame = Frame(bustimeframe, bg = 'steelblue2', bd = 0, highlightthickness = 0)
                    bus2frame.place(relx = .5, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    est = Label(bus2frame, bg = bus2frame['bg'], bd = 0, highlightthickness = 0, font = 'Arial 15', text = 'No Estimate\nAvailable!')
                    est.place(relx = 0.5, rely = 0.5, anchor = CENTER, relwidth = .9, relheight = .9)
                    self.bustimes.append(bus2frame)
                    self.bustimes.append(est)
                else:
                    timehr = int(x['NextBus2']['EstimatedArrival'][11:13])
                    if (timemin < currmin and timehr > currhr) or (timemin < currmin and timehr == 0 and currhr == 11):
                        if timemin + 60 > currmin:
                            arrtime2 = str(timemin + 60 - currmin) + 'm'
                        else:
                            arrtime2 = '>1h'
                    elif timemin < currmin and timehr == currhr:
                        arrtime2 = 'Arr'
                    elif timemin == currmin:
                        arrtime2 = 'Arr'
                    else:
                        arrtime2 = str(timemin - currmin) + 'm'
                    bus2frame = Frame(bustimeframe, bg = 'chartreuse2' if x['NextBus2']['Load'] == 'SEA' else 'yellow2' if x['NextBus2']['Load'] == 'SDA' else 'red2', bd = 0, highlightthickness = 0)
                    bus2frame.place(relx = .5, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    bus2time = Label(bus2frame, bg = bus2frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '20') if arrtime2 != 'Arr' else ('Arial', '20', 'bold'), text = arrtime2 if arrtime2 == 'Arr' else '~'+arrtime2)
                    bus2time.place(relx = .5, rely = .15, anchor = CENTER, relheight = .2, relwidth = .9)
                    singledoubledeck = Label(bus2frame, bg = bus2frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Double Decker' if x['NextBus2']['Type'] == 'DD' else 'Single Decker' if x['NextBus2']['Type'] == 'SD' else 'Long and Bendy')
                    singledoubledeck.place(relx = .5, rely = .4, anchor = CENTER, relheight = .25, relwidth = .9)
                    wab = Label(bus2frame, bg = bus2frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Wheelchairs allowed!' if x['NextBus2']['Feature'] == 'WAB' else 'No wheelchairs!')
                    wab.place(relx = .5, rely = .7, anchor = CENTER, relheight = .25, relwidth = .9)
                    self.bustimes.append(bus2time)
                    self.bustimes.append(bus2frame)
                    self.bustimes.append(singledoubledeck)
                    self.bustimes.append(wab)
                skip = False
                try:
                    timemin = int(x['NextBus3']['EstimatedArrival'][14:16])
                except ValueError:
                    skip = True
                if skip:
                    bus3frame = Frame(bustimeframe, bg = 'steelblue2', bd = 0, highlightthickness = 0)
                    bus3frame.place(relx = .8, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    est = Label(bus3frame, bg = bus3frame['bg'], bd = 0, highlightthickness = 0, font = 'Arial 15', text = 'No Estimate\nAvailable!')
                    est.place(relx = 0.5, rely = 0.5, anchor = CENTER, relwidth = .9, relheight = .9)
                    self.bustimes.append(bus3frame)
                    self.bustimes.append(est)
                else:
                    timehr = int(x['NextBus3']['EstimatedArrival'][11:13])
                    if (timemin < currmin and timehr > currhr) or (timemin < currmin and timehr == 0 and currhr == 11):
                        if timemin + 60 > currmin:
                            arrtime3 = str(timemin + 60 - currmin) + 'm'
                        else:
                            arrtime3 = '>1h'
                    elif timemin < currmin and timehr == currhr:
                        arrtime3 = 'Arr'
                    elif timemin == currmin:
                        arrtime3 = 'Arr'
                    else:
                        arrtime3 = str(timemin - currmin) + 'm'
                    bus3frame = Frame(bustimeframe, bg = 'chartreuse2' if x['NextBus3']['Load'] == 'SEA' else 'yellow2' if x['NextBus3']['Load'] == 'SDA' else 'red2', bd = 0, highlightthickness = 0)
                    bus3frame.place(relx = .8, rely = .5, anchor = W, relheight = 1, relwidth = .2)
                    bus3time = Label(bus3frame, bg = bus3frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '20') if arrtime3 != 'Arr' else ('Arial', '20', 'bold'), text = arrtime3 if arrtime3 == 'Arr' else '~'+arrtime3)
                    bus3time.place(relx = .5, rely = .15, anchor = CENTER, relheight = .2, relwidth = .9)
                    singledoubledeck = Label(bus3frame, bg = bus3frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Double Decker' if x['NextBus3']['Type'] == 'DD' else 'Single Decker' if x['NextBus3']['Type'] == 'SD' else 'Long and Bendy')
                    singledoubledeck.place(relx = .5, rely = .4, anchor = CENTER, relheight = .25, relwidth = .9)
                    wab = Label(bus3frame, bg = bus3frame['bg'], bd = 0, highlightthickness = 0, font = ('Arial Narrow', '15'), text = 'Wheelchairs allowed!' if x['NextBus3']['Feature'] == 'WAB' else 'No wheelchairs!')
                    wab.place(relx = .5, rely = .7, anchor = CENTER, relheight = .25, relwidth = .9)
                    self.bustimes.append(bus3time)
                    self.bustimes.append(bus3frame)
                    self.bustimes.append(singledoubledeck)
                    self.bustimes.append(wab)
                count += 1
            elif count == 0:
                prevbutton = Label(self.bustimesframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '<', font = ('Arial Narrow', '10'))
                prevbutton.bind('<Button-1>', partial(self.showbustimesE, stopcode, True, str(start - 5)+'-'+str(stop - 5)))
                prevbutton.place(relx = .5, rely = .96, x = -5, anchor = NE, relheight = .03, relwidth = .03)
                self.bustimes.append(prevbutton)
                count = 1
            elif count < start-1:
                count += 1
            elif count == stop:
                nextbutton = Label(self.bustimesframe, bd = .5, highlightthickness = 0, relief = SOLID, bg = 'white', text = '>', font = ('Arial Narrow', '10'))
                nextbutton.bind('<Button-1>', partial(self.showbustimesE, stopcode, True, str(start + 5)+'-'+str(stop + 5)))
                nextbutton.place(relx = .5, rely = .96, x = 5, anchor = NW, relheight = .03, relwidth = .03)
                self.bustimes.append(nextbutton)
                break

    def simpleSearch(self, items, inputstr, capmatters = False, special = -1):
        if special != -1:
            items = list(enumerate(zip(items, special)))
            for a in range(len(items)):
                items[a] = tuple([items[a][0], items[a][1][0], items[a][1][1]])
        else:
            items = enumerate(items)
        newitems = []
        for x in items:
            if len(newitems) > 0:
                ind = 0
                for y in newitems:
                    if x[1] < y[1]:
                        newitems.insert(ind, x)
                        break
                    elif ind + 1 == len(newitems):
                        newitems.append(x)
                    else:
                        ind += 1
            else:
                newitems.append(x)
        resultlist = []
        no = []
        end1 = 0
        end2 = 0
        for x in newitems:
            if special == -1:
                i = x[1]
                en = x[0]
                if capmatters == False:
                    newi = i.lower()
                    inputstr = inputstr.lower()
                else:
                    newi = i
                if newi == inputstr:
                    resultlist.insert(end1, i)
                    no.insert(end1, en)
                    end1 += 1
                    end2 += 1
                else:
                    if re.search('^'+inputstr, newi):
                        resultlist.insert(end2, i)
                        no.insert(end2, en)
                        end2 += 1
                    elif re.search(' '+inputstr+' |'+inputstr+'$', newi):
                        resultlist.append(i)
                        no.append(en)
            else:
                i = x[1]
                i2 = x[2]
                en = x[0]
                if capmatters == False:
                    newi = i.lower()
                    inputstr = inputstr.lower()
                    newi2 = i2.lower()
                else:
                    newi = i
                    newi2 = i2
                if newi == inputstr or newi2 == inputstr:
                    resultlist.insert(end1, i)
                    no.insert(end1, en)
                    end1 += 1
                    end2 += 1
                else:
                    if re.search('^'+inputstr, newi) or re.search('^'+inputstr, newi2):
                        resultlist.insert(end2, i)
                        no.insert(end2, en)
                        end2 += 1
                    elif re.search(' '+inputstr+' |'+inputstr+'$', newi) or re.search(' '+inputstr+' |'+inputstr+'$', newi2):
                        resultlist.append(i)
                        no.append(en)
        return resultlist, no

if __name__ == '__main__':
    app = App()
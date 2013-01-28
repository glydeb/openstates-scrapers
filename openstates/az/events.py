import datetime
import re

from lxml import html

from billy.scrape import NoDataForPeriod
from billy.scrape.events import EventScraper, Event


class AZEventScraper(EventScraper):
    """
    Arizona Event Scraper, gets interim committee, agendas, floor calendars
    and floor activity events
    """
    jurisdiction = 'az'

    _chamber_short = {'upper': 'S', 'lower': 'H'}
    _chamber_long = {'upper': 'Senate', 'lower': 'House'}

    def get_session_id(self, session):
        """
        returns the session id for a given session
        """
        return self.metadata['session_details'][session]['session_id']

    def scrape(self, chamber, session):
        if chamber == "other":
            return
        """
        given a chamber and session returns the events
        """
        try:
            session_id = self.get_session_id(session)
        except KeyError:
            raise NoDataForPeriod(session)

        # this will only work on the latest regular or special session
        # 103 is fortyninth - ninth special session 102 is session_ID for
        # fiftieth
        # we can get old events with some hassle but we cant change what has
        # already happened so why bother?
        if session_id == 103 or session_id < 102:
            raise NoDataForPeriod(session)

        # http://www.azleg.gov/CommitteeAgendas.asp?Body=H
        self.scrape_committee_agendas(chamber, session)
        # http://www.azleg.gov/InterimCommittees.asp
        # self.scrape_interim_events(chamber, session)

    def scrape_committee_agendas(self, chamber, session):
        """
        Scrape upper or lower committee agendas
        """
        # could use &ShowAll=ON doesn't seem to work though
        url = 'http://www.azleg.gov/CommitteeAgendas.asp?Body=%s' % \
                                          self._chamber_short[chamber]
<<<<<<< Updated upstream
        agendas = self.urlopen(url)
        root = html.fromstring(agendas)
        if chamber == 'upper':
            event_table = root.xpath('//table[@id="body"]/tr/td/table[2]/tr'
                                     '/td/table/tr/td/table')[0]
        else:
            event_table = root.xpath('//table[@id="body"]/tr/td/table[2]/tr'
=======
        html_ = self.urlopen(url)
        doc = html.fromstring(html_)
        if chamber == 'upper':
            event_table = doc.xpath('//table[@id="body"]/tr/td/table[2]/tr'
                                     '/td/table/tr/td/table')[0]
        else:
            event_table = doc.xpath('//table[@id="body"]/tr/td/table[2]/tr'
>>>>>>> Stashed changes
                                     '/td/table/tr/td/table/tr/td/table')[0]
        for row in event_table.xpath('tr')[2:]:
            # Agenda Date, Committee, Revised, Addendum, Cancelled, Time, Room,
            # HTML Document, PDF Document for house
            # Agenda Date, Committee, Revised, Cancelled, Time, Room,
            # HTML Document, PDF Document for senate
<<<<<<< Updated upstream
            text = [ x.text_content().strip() for x in row.xpath('td') ]
=======
            text = [x.text_content().strip() for x in row.xpath('td')]
>>>>>>> Stashed changes
            when, committee = text[0:2]
            if chamber == 'upper':
                time, room = text[4:6]
                link = row[6].xpath('string(a/@href)')
            else:
                time, room = text[5:7]
                link = row[7].xpath('string(a/@href)')
            if 'NOT MEETING' in time or 'CANCELLED' in time:
                continue
            time = re.match('(\d+:\d+ (A|P))', time)
            if time:
                when = "%s %sM" % (text[0], time.group(0))
                when = datetime.datetime.strptime(when, '%m/%d/%Y %I:%M %p')
            else:
                when = text[0]
                when = datetime.datetime.strptime(when, '%m/%d/%Y')

<<<<<<< Updated upstream
            when = self._tz.localize(when)

=======
>>>>>>> Stashed changes
            title = "Committee Meeting:\n%s %s %s\n" % (
                                              self._chamber_long[chamber],
                                              committee, room)
            agenda_info = self.parse_agenda(chamber, link)

            description = agenda_info['description']
            member_list = agenda_info['member_list']
<<<<<<< Updated upstream
            for member in member_list:
                member.update(participant_type='legislator',
                              type='participant')
            meeting_type = agenda_info['meeting_type']
            agenda_items = agenda_info['agenda_items']
            related_bills= agenda_info['related_bills']
            other = agenda_info['other']

            event = Event(session, when, 'committee:meeting', title,
                          location=room, link=link, details=description) #,
                          #agenda=agenda_items)

            event.add_participant('host', committee, 'committee',
                                  chamber=chamber)

            for i in range(0, len(related_bills)):
                bill = related_bills[i]
                desc = description[i]
                event.add_related_bill(
                    bill,
                    description=desc,
                    type="consideration"
                )

            event['participants'].extend(member_list)
            event.add_source(url)
            event.add_source(link)
=======
            related_bills = agenda_info['related_bills']

            event = Event(session, when, 'committee:meeting', title,
                          location=room, link=link, details=description,
                          related_bills=related_bills)
            event.add_participant('host', committee, 'committee',
                                  chamber=chamber)

            event['participants'].extend(member_list)
            event.add_source(url)
            event.add_source(link)
            # print event['when'].timetuple()
            # import ipdb;ipdb.set_trace()
>>>>>>> Stashed changes
            self.save_event(event)

    def parse_agenda(self, chamber, url):
        """
        parses the agenda detail and returns the description, participants, and
        any other useful info
        self.parse_agenda(url)--> (desc='', who=[], meeting_type='', other={})
        """
<<<<<<< Updated upstream
        agenda_detail = self.urlopen(url)
        root = html.fromstring(agenda_detail)
        div = root.xpath('//div[@class="Section1"]')[0]
        # probably committee + meeting_type?
        meeting_type = div.xpath('string(//p'
                                 '[contains(a/@name, "Joint_Meeting")])')
        members = root.xpath('//p[contains(a/@name, "Members")]')
        if members:
            members = members[0]
        else:
            members = root.xpath('//p[contains(span/a/@name, "Members")]')[0]
        if chamber == 'lower':
            name_role = re.compile(r'(\w+.\s\w+\s?[a-zA-z]*(?!<.))'
                                    ',?\s?(\w+-?\w+)?')
        else:
            name_role = re.compile(r'(\w+),?\s*(\w+-?\w+)?')
        other = {}
        member_list = []
        while members.tag == 'p':
            text = members.text_content().strip()
            if text == '': break
            found = name_role.findall(text)
            if found:
                for name, role in found:
                    if name == 'SENATORS' or name == 'Members': continue
                    person = {"type": role or "member",
                              "participant": name,
=======
        html_ = self.urlopen(url)
        doc = html.fromstring(html_)

        # Related bills
        related_bills = []
        for tr in doc.xpath('//h3[contains(., "Bills")]/../../../../tr'):
            related_bill = {}
            bill_id = tr[1].text_content().strip()
            if not bill_id or bill_id[0] not in 'HS':
                continue
            related_bill['bill_id'] = bill_id
            description = tr[3].text_content().strip()
            description = re.sub(r'\s+', ' ', description)
            related_bill['description'] = description
            related_bill['type'] = 'consideration'
            related_bills.append(related_bill)

        div = doc.xpath('//div[@class="Section1"]')[0]
        # probably committee + meeting_type?
        meeting_type = div.xpath('string(//p'
                                 '[contains(a/@name, "Joint_Meeting")])')
        members = doc.xpath('//p[contains(a/@name, "Members")]')
        if members:
            members = members[0]
        else:
            members = doc.xpath('//p[contains(span/a/@name, "Members")]')[0]
        other = {}
        member_list = []
        while members.tag == 'p':
            text = members.text_content().strip().replace(u'\xa0', u' ')
            if text == '':
                break
            names = re.split(r'\s{5,}', text)
            if names:
                for name in names:
                    name = re.sub(r'\s+', ' ', name)
                    if ',' in name:
                        name, role = name.split(',')
                        role = role.lower()
                    else:
                        role = None
                    if name == 'SENATORS' or name == 'Members':
                        continue
                    if role in ['chair', 'chairman']:
                        role = 'chair'
                    else:
                        role = 'participant'
                    person = {"type": role,
                              "participant": name,
                              "participant_type": 'legislator',
>>>>>>> Stashed changes
                              "chamber": chamber}
                    member_list.append(person)
            members = members.getnext()
        description = ""
        agenda_items = div.xpath('//p[contains(a/@name, "AgendaItems")]'
                                '/following-sibling::table[1]')
        if agenda_items:
            agenda_items = [tr.text_content().strip().replace("\r\n", "")
                            for tr in agenda_items[0].getchildren()
                            if tr.text_content().strip()]
            description = ",\n".join(agenda_items)
        bill_list = div.xpath('//p[contains(a/@name, "Agenda_Bills")]'
                                '/following-sibling::table[1]')
        if bill_list:
            try:
                bill_list = [tr[1].text_content().strip() + " " +
                         tr[3].text_content().strip().replace("\r\n", "")
                         for tr in bill_list[0].xpath('tr')
                         if tr.text_content().strip()]
            except IndexError:
                bill_list = [tr.text_content().strip().replace("\r\n", "")
                            for tr in bill_list[0].getchildren()
                            if tr.text_content().strip()]

            bill_list = ",\n".join(bill_list)
            description = description + bill_list

<<<<<<< Updated upstream
        bills_for_consideration = []

        related_bills = root.xpath("//table[@class='MsoNormalTable']//tr")
        for tr in related_bills:
            bill_id = tr.xpath("./td")[1].text_content().strip()
            if bill_id == "" or bill_id.lower() == "bills":
                continue
            if bill_id[0] != "H" and bill_id[0] != "S":
                continue

            bills_for_consideration.append(bill_id)

        return {
            "description" : description,
            "member_list" : member_list,
            "meeting_type": meeting_type,
            "agenda_items": agenda_items,
            "related_bills": bills_for_consideration,
            "other" : other
=======
        return {
            "description": description,
            "member_list": member_list,
            "meeting_type": meeting_type,
            "agenda_items": agenda_items,
            "related_bills": related_bills,
            "other": other
>>>>>>> Stashed changes
        }

    def scrape_interim_events(self, chamber, session):
        """
        Scrapes the events for interim committees
        """
        session_id = self.get_session_id(session)
        url = 'http://www.azleg.gov/InterimCommittees.asp?Session_ID=%s' % session_id
        # common xpaths
        agendas_path = '//table[contains(' \
                       'tr/td/div[@class="ContentPageTitle"]/text(), "%s")]'

<<<<<<< Updated upstream
        event_page = self.urlopen(url)
        root = html.fromstring(event_page)
        table = root.xpath(agendas_path % "Interim Committee Agendas")
=======
        html_ = self.urlopen(url)
        doc = html.fromstring(html_)
        table = doc.xpath(agendas_path % "Interim Committee Agendas")
>>>>>>> Stashed changes
        if table:
            rows = table[0].xpath('tr')
            for row in rows[2:]:
                pass

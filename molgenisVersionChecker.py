import requests
import molgenis
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from logWriter import LogWriter


class MolgenisVersionChecker():
    def __init__(self, range):
        # range should be list [first server, last server]
        print("Checking all Molgenis VM's in range: ", range[0], "-", range[1])
        self.range = range
        print("Creating log file (log.txt)...")
        self.logs = LogWriter("logx.txt")
        self.logs.reset("Server\tMessage\tVersion")

    def get_session(self, host):
        print("Connecting to: ", host)
        session = molgenis.Session("https://" + host + "/api/")
        return session

    def get_version_response(self, session, x):
        print("Checking version of: Molgenis" + x)
        try:
            version = session.get_molgenis_version()
            self.logs.write_row('molgenis' + x + "\t\t" + version['molgenisVersion'])
        except requests.exceptions.HTTPError as e:
            host = "http://molgenis" + str(x) + ".gcc.rug.nl"
            try:
                version = self.get_page_footer(host)
                self.logs.write_row("molgenis{}\t{}\t{}".format(x, str(e), version))
            except:
                self.logs.write_row(
                    'molgenis' + x + "\tConnection error: server behind firewall/molgenis not deployed/Ancient molgenis version\t")
        except requests.packages.urllib3.exceptions.SSLError as e:
            host = "http://molgenis" + str(x) + ".gcc.rug.nl"
            self.logs.write_row("molgenis{}\t{}\t{}".format(x, str(e), version))
        except requests.exceptions.ConnectionError as e:
            if "doesn't match" in str(e):
                host = str(e).split('\'')[-2]
                version = self.get_page_footer("http://"+host)
                self.logs.write_row("molgenis{}-{}\t{}\t{}".format(x, host, str(e), version))

            else:
                host = "http://molgenis" + str(x) + ".gcc.rug.nl"
                try:
                    version = self.get_page_footer(host)
                    self.logs.write_row("molgenis{}\t{}\t{}".format(x, str(e), version))
                except:
                    self.logs.write_row(
                    'molgenis' + x + "\tConnection error: server behind firewall/molgenis not deployed/Ancient molgenis version\t")

    def check_version(self):
        for x in range(self.range[0], self.range[1] + 1):
            if x < 10:
                x = "0" + str(x)
            else:
                x = str(x)
            host = "molgenis" + str(x) + ".gcc.rug.nl"
            session = self.get_session(host)
            self.get_version_response(session, x)

    def get_page_footer(self, url):
        soup = BeautifulSoup(urlopen(url), "lxml")
        result = soup.find("div", {"class":["footer", "row footer"]})
        if result == None:
            result = soup.find("div", {"id":"molgenis-footer"})
        if result != None:
            pattern = r'version ([\w\.-]+)[ buil|\.<br/>]+'
            matches = re.search(pattern, str(result))
            if matches != None:
                return matches.group(1)


if __name__ == "__main__":
    vc = MolgenisVersionChecker([1, 115])
    vc.check_version()
    vc.logs.close_logs()
    print("Done")

from advUtils.core.decorators import experimental
from advUtils.miscellaneous import Utils
from advUtils.system import TTS


class QPythonCode(object):
    def __init__(self, py_code):
        self._code = py_code

    @experimental
    def import_(self):
        pass

    def execute(self, filename, loc=None, glob=None):
        """
        Execute code with the given filename

        Examples
        --------
        Example 1:

        >>> code = 'print("Hello World")'
        >>> pycode = QPythonCode(code)
        >>> pycode.execute("Test.py")

        Example 2:

        >>> filename = "Test.py"  # Replace with your own filename you want to execute
        >>> with open(filename) as file:
        ...     code = file.read()
        ...     pycode = QPythonCode(code)
        ...     pycode.execute(filename)

        :param loc:
        :param glob:
        :param filename: The filename to use for the code execution
        :returns: The compiled code object
        """

        if glob is None:
            glob = {}
        if loc is None:
            loc = {}

        glob = glob.copy()
        loc = loc.copy()
        ccode = compile(self._code, filename, "exec")
        exec(ccode, __globals=glob, __locals=loc)
        return ccode, glob, loc

    @experimental
    def compile(self, filename, mode, optimize=2):
        ccode = compile(self._code, filename, mode, optimize=optimize)
        return ccode


class HtmlCode(object):
    def __init__(self, html_data):
        self._data = html_data

        from bs4 import BeautifulSoup
        self.bs = BeautifulSoup
        self.soup = self.bs(self._data, features="lxml")

    def find_all(self, tag, attrs):
        return self.soup.findAll(tag, attrs=attrs)

    def find_all_links(self, http=False, https=False, ftp=False, ftps=False):
        """
        Find links in http[s] and / or ftp[s], if all arguments are False, it returns all links

        :param http:
        :param https:
        :param ftp:
        :param ftps:
        :return:
        """

        # Import REGEX (re) module
        import re

        # http:// and https://
        if http:
            if https:
                h = "(^http://)|(^https://)"
            else:
                h = "(^http://)"
        elif https:
            h = "(^https://)"
        else:
            h = ""

        # fps:// and ftps://
        if ftp:
            if ftps:
                f = "(^ftp://)|(^ftps://)"
            else:
                f = "(^ftp://)"
        elif ftps:
            f = "(^ftps://)"
        else:
            f = ""

        # Find with regex and return list of urls
        if h:
            if f:
                # noinspection RegExpDuplicateAlternationBranch
                return [url.get("href") for url in self.find_all('a', attrs={'href': re.compile(f"({h})|({f})")})]
            else:
                return [url.get("href") for url in self.find_all('a', attrs={'href': re.compile(f"{h}")})]
        elif f:
            return [url.get("href") for url in self.find_all('a', attrs={'href': re.compile(f"{f}")})]
        else:
            return [url.get("href") for url in self.find_all('a', attrs={'href': re.compile(".*")})]

    def find_links_by_regex(self, regex):
        import re
        return [url.get("href") for url in self.find_all('a', attrs={'href': re.compile(regex)})]


if __name__ == '__main__':
    import urllib.request


    def test_tts():
        tts = TTS("en")

        print("Checking for Ubuntu MATE releases")
        tts.speak("Checking for Ubuntu MATE releases")

        u = urllib.request.urlopen("http://cdimage.ubuntu.com/ubuntu-mate/releases/")
        html = u.read()
        code = HtmlCode(html)
        print(code.find_all_links())
        print(code.find_all_links(http=True))

        releases = code.find_links_by_regex("((\\d)*\\.\\d\\d\\.(\\d)*/)|((\\d)*\\.\\d\\d)/")
        print(releases)

        print("")

        release = releases[0]

        print(f"Selected {release} release")
        tts.speak(f"Selected {release} release")

        u2 = urllib.request.urlopen("http://cdimage.ubuntu.com/ubuntu-mate/releases/" + release + "/release")
        html2 = u2.read()
        code2 = HtmlCode(html2)
        print(f"All links in {release} are {code2.find_all_links()}")
        print(f"All http[s] links in {release} are {code2.find_all_links(http=True, https=True)}")

        isos_ = code2.find_links_by_regex("\\.iso$")
        print(f"Before removing dups: {isos_}")
        isos = Utils.remove_duplicates(isos_.copy())
        print(f"After removing dups:  {isos}")

        print("\nThe 'isos' list have NONE duplicates" if isos == isos_ else "\nThe 'isos' list has duplicates")
        tts.speak("\nThe 'isos' list have NONE duplicates" if isos == isos_ else "\nThe 'isos' list has duplicates")

        try:
            for iso in isos:
                import re
                print("")
                print(f"Checking: {iso}")
                abc = re.search(
                    r"((?:(?:.*)(?:-(?:.*)).*)|(?:.*))-((?:(?:\d)*\.\d\d\.(?:\d)*)|(?:(?:\d)*\.\d\d))-((?:(?:.*)(?:-"
                    r"(?:.*))*)|(?:.*))(?:-(.*))\\.iso",
                    iso)
                print(abc.groups())
                print(f"________________________________")
                print(f"  Subject    |      Value       ")
                print(f"_____________|__________________")
                print(f"Edition      | {abc.groups()[0]}")
                print(f"Version      | {abc.groups()[1]}")
                print(f"Type         | {abc.groups()[2]}")
                print(f"Architecture | {abc.groups()[3]}")
                print(f"_____________|__________________")

            print("Ended successfully checking Ubuntu MATE Releases")
            tts.speak("Ended successfully checking Ubuntu MATE Releases")
        except Exception as e:
            tts.speak(f"Something went wrong while parsing the iso information: {e.__class__.__name__}, {e.__str__()}")


    def test_pycode():
        code = \
            """
import random

print("Hallo")
a = "test" + str(random.randint(100, 999))
b = True
if b:
    print(f"This is {a}")
"""
        pycode = QPythonCode(code)
        pycode.execute("someTest.py")


    test_pycode()

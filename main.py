import http.client
from html.parser import HTMLParser
import re
import subprocess

class CBSClient:

    def __init__(self, printer, year):
        # Interfaz de impresora
        self.printer = printer

        # Cargando publicaciones
        self.connection = http.client.HTTPConnection("cbs.cl")
        self.connection.request("GET", "/publicaciones.php?5-ordenes-del-dia")
        data = self.connection.getresponse()

        # Alimentando el parser
        self.parser = CBSParser(self, year)
        self.parser.feed(data.read().decode("utf-8"))

    def handle_download(self, url):
        print("Handling {}".format(url))

        if self.check_not_printed_file(url):
            print("Not printed. Downloading...")

            self.connection.request("GET", "/" + url)
            data = self.connection.getresponse()

            path = "tmp/{}.pdf".format(re.sub('[\.\&\?]', '', url))

            open(path, "wb").write(data.read())

            print("Download complete.")

            self.printer.print_file(path)


    def check_not_printed_file(self, file_url):
        f = open("data")

        for line in f.readlines():
            if file_url == line.strip():
                return False

        f.close()
        open("./data", "a").write("\n" + file_url)

        return True

class CBSParser(HTMLParser):
    def __init__(self, client, year):
        super().__init__()

        self.client = client
        self.open_h3_tag = False
        self.year = year
        self.current_year = float("inf")

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    test = re.match("descargar.php?.*?&publicacion", attr[1])

                    if test and self.year == self.current_year:
                        print(self.year, self.current_year)
                        self.client.handle_download(test.group(0))
        elif tag == "h3":
            self.open_h3_tag = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self.open_h3_tag = False

    def handle_data(self, data):
        try:
            self.current_year = int(data)
        except ValueError:
            pass



class PDFPrinter:

    def print_file(self, path):
        subprocess.call("SumatraPDF -print-to-default -exit-when-done {}".format(path), shell=True)

if __name__ == "__main__":
    CBSClient(PDFPrinter(), 2015)

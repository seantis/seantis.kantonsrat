from io import BytesIO
from pdfdocument.document import PDFDocument, ReportingDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents

from seantis.plonetools import tools


class Template(ReportingDocTemplate):

    def afterFlowable(self, flowable):

        ReportingDocTemplate.afterFlowable(self, flowable)

        if hasattr(flowable, 'toc_level'):
            text = flowable.getPlainText()
            self.notify('TOCEntry', (flowable.toc_level, text, self.page))


class PDF(PDFDocument):

    def __init__(self, *args, **kwargs):
        self.doc = Template(*args, **kwargs)
        self.doc.PDFDocument = self
        self.story = []

        self.font_name = kwargs.get('font_name', 'Helvetica')
        self.font_size = kwargs.get('font_size', 9)

    def table_of_contents(self):
        self.toc = TableOfContents()
        self.story.append(self.toc)

    def h1(self, text, style=None):
        super(PDF, self).h1(text, style)
        if hasattr(self, 'toc'):
            self.story[-1].toc_level = 0


class Report(object):

    def __init__(self):
        self.file = BytesIO()
        self.pdf = PDF(self.file)
        self.pdf.init_report()

    def translate(self, text):
        return tools.translator(self.request, 'seantis.kantonsrat')(text)

    def populate(self):
        raise NotImplementedError

    def build(self, context, request):
        self.context = context
        self.request = request
        self.populate()
        self.pdf.generate()
        self.file.seek(0)
        return self.file

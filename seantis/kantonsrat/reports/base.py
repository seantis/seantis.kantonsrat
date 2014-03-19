from io import BytesIO
from pdfdocument.document import (
    PDFDocument,
    ReportingDocTemplate,
    PageTemplate,
    NextPageTemplate,
    dummy_stationery,
    Frame,
    cm
)
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
        self.show_boundaries = True

        self.font_name = kwargs.get('font_name', 'Helvetica')
        self.font_size = kwargs.get('font_size', 9)

        self.margin_left = 3.5*cm
        self.margin_top = 5.2*cm
        self.margin_bottom = 4*cm
        self.margin_right = 1.5*cm

    def table_of_contents(self):
        self.toc = TableOfContents()
        self.story.append(self.toc)

    def h1(self, text, style=None):
        super(PDF, self).h1(text, style)
        if hasattr(self, 'toc'):
            self.story[-1].toc_level = 0

    def init_report(self, page_fn=dummy_stationery, page_fn_later=None):
        frame_kwargs = {
            'showBoundary': self.show_boundaries,
            'leftPadding': 0,
            'rightPadding': 0,
            'topPadding': 0,
            'bottomPadding': 0,
        }

        self.page_width, self.page_height = self.doc.pagesize

        # x and y start at the lower left corner
        full_frame = Frame(
            x1=self.margin_left,
            y1=self.margin_bottom,
            width=self.page_width - self.margin_left - self.margin_right,
            height=self.page_height - self.margin_top - self.margin_bottom,
            **frame_kwargs
        )

        self.doc.addPageTemplates([
            PageTemplate(
                id='First',
                frames=[full_frame],
                onPage=page_fn),
            PageTemplate(
                id='Later',
                frames=[full_frame],
                onPage=page_fn_later or page_fn),
        ])
        self.story.append(NextPageTemplate('Later'))
        self.generate_style(font_size=8)


class Report(object):

    def __init__(self):
        self.file = BytesIO()
        self.pdf = PDF(self.file)
        self.pdf.init_report(
            page_fn=self.first_page, page_fn_later=self.later_page
        )

    def first_page(self, canvas, doc):
        pass

    def later_page(self, canvas, doc):
        pass

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

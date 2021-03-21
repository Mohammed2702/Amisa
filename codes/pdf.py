from django.template.loader import get_template, render_to_string
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404

from xhtml2pdf import pisa
from io import BytesIO

from codes.models import CodeGroup, Code


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GeneratePDFView(View):

	def get(self, request, slug, *args, **kwargs):
		code_batch = get_object_or_404(CodeGroup, slug=slug)
		code = Code.objects.filter(code_group=code_batch)

		template_name = 'Home/code-batch-sheet.html'
		context = {
		    'code_batch': code_batch,
		    'codes': code
		}

		template = get_template(template_name)

		html = template.render(context)
		pdf = render_to_pdf(template_name, context)
		return HttpResponse(pdf, content_type='application/pdf')

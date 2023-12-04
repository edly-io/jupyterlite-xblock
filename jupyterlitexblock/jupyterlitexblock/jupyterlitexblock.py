"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources,os
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from django.core.files.base import ContentFile
from xblock.fields import Scope, String
from django.template import Context, Template
import urllib.parse
import logging
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage
from webob import Response


log = logging.getLogger(__name__)


class JupterLiteXBlock(XBlock):
    """
       EdX XBlock for embedding JupyterLite, allowing learners to interact with Jupyter notebooks.
       Instructors can configure JupyterLite settings in Studio, and learners access notebooks in the LMS 
    """


    jupyterlite_url = String(
        display_name="JupyterLite Service URL",
        help="The URL of the JupyterLite service",
        scope=Scope.settings,
        default="http://localhost:9500/lab/"
    )
    default_notebook = String(
        display_name="Default Notebook",
        scope=Scope.content,
        help="The default notebook for the JupyterLite service",
        default=""
    )
    display_name = String(
        display_name=("JupyterLite "),
        help=("Display name for this module"),
        default="JupyterLite Notebook",
        scope=Scope.settings
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        rendered_template = template.render(Context({'context': context}))
        return rendered_template
    
    def student_view(self, context=None):
        file_name = self.default_notebook
        base_url = self.jupyterlite_url
        jupyterlite_iframe = '<iframe src="{}?fromURL={}" width="100%" height="600px" style="border: none;"></iframe>'.format(base_url, file_name)
        html = self.resource_string("static/html/jupyterlitexblock.html").format(jupyterlite_iframe=jupyterlite_iframe, self=self)
        frag = Fragment(html)
        frag.initialize_js('JupterLiteXBlock')
        return frag

    @staticmethod
    def json_response(data):
        return Response(
            json.dumps(data), content_type="application/json", charset="utf8"
        )
    
    def studio_view(self, context=None):
        studio_context = {
            "jupyterlite_url": self.fields["jupyterlite_url"],
            "default_notebook": self.fields["default_notebook"]
        } 
        studio_context.update(context or {})
        template = self.render_template("static/html/upload.html", studio_context)
        frag = Fragment(template)
        frag.add_javascript(self.resource_string("static/js/src/jupyterlitexblock.js"))
        frag.initialize_js('JupterLiteXBlock')
        return frag
    
    def save_file(self, uploaded_file):
        path = default_storage.save(f'static/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        scheme = "https" if settings.HTTPS == "on" else "http"
        root_url = f'{scheme}://{settings.CMS_BASE}'
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        uploaded_file_url = root_url+tmp_file.replace('/openedx','')
        return uploaded_file_url

    @XBlock.handler
    def studio_submit(self, request, _suffix):
        """
        Handle form submission in Studio.
        """
        get_url = request.params.get("jupyterlite_url",None)
        notebook = request.params.get("default_notebook").file
        self.jupyterlite_url = get_url
        self.default_notebook = self.save_file(notebook)
        response = {"result": "success", "errors": []}
        return self.json_response(response)

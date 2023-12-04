"""XBlock for embedding JupyterLite in Open edX."""

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


@XBlock.wants("settings")
class JupterLiteXBlock(XBlock):
    """
       EdX XBlock for embedding JupyterLite, allowing learners to interact with Jupyter notebooks.
       Instructors can configure JupyterLite settings in Studio, and learners access notebooks in the LMS 
    """


    jupyterlite_url = String(
        display_name="JupyterLite Service URL",
        help="The URL of the JupyterLite service",
        scope=Scope.settings,
        default="http://jupyterlite.local.overhang.io:9500/lab/index.html"
    )
    default_notebook = String(
        display_name="Default Notebook",
        scope=Scope.content,
        help="The default notebook for the JupyterLite service",
        default=""
    )
    display_name = String(
        display_name=("JupyterLite"),
        help=("Display name for this module"),
        default="JupyterLite Notebook",
        scope=Scope.settings
    )

    def notebook_location(self):
        """
        Notebooks will be stored in a media folder with this name
        """
        return self.xblock_settings.get("LOCATION", "jupyterlite_notebooks")

    @property
    def xblock_settings(self):
        """
        Return a dict of settings associated to this XBlock.
        """
        settings_service = self.runtime.service(self, "settings") or {}
        if not settings_service:
            return {}
        return settings_service.get_settings_bucket(self)

    @property
    def folder_base_path(self):
        """
        Path to the folder where notebooks will be saved.
        """
        return os.path.join(self.notebook_location(), self.location.block_id)

    @property
    def storage(self):
        """
        Return the storage backend used to store the assets of this xblock. This is a cached property.
        """
        if not getattr(self, "_storage", None):

            def get_default_storage(_xblock):
                return default_storage

            storage_func = self.xblock_settings.get("STORAGE_FUNC", get_default_storage)
            if isinstance(storage_func, str):
                storage_func = import_string(storage_func)
            self._storage = storage_func(self)

        return self._storage

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        rendered_template = template.render(Context(context))
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
        notebook_name = os.path.basename(self.default_notebook) if self.default_notebook else ""
        studio_context = {
            "jupyterlite_url": self.jupyterlite_url,
            "notebook_name": notebook_name,
        } 
        studio_context.update(context or {})
        template = self.render_template("static/html/upload.html", studio_context)
        frag = Fragment(template)
        frag.add_javascript(self.resource_string("static/js/src/jupyterlitexblock.js"))
        frag.initialize_js('JupterLiteXBlock')
        return frag
    
    def save_file(self, uploaded_file):
        path = self.storage.save(f'{self.folder_base_path}/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        uploaded_file_url = self.storage.url(path)
        return uploaded_file_url

    @XBlock.handler
    def studio_submit(self, request, _suffix):
        """
        Handle form submission in Studio.
        """
        self.jupyterlite_url = str(request.params.get("jupyterlite_url", ""))
        notebook = request.params.get("default_notebook").file
        self.default_notebook = self.save_file(notebook)
        response = {"result": "success", "errors": []}
        return self.json_response(response)

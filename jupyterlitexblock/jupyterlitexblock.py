"""XBlock for embedding JupyterLite in Open edX."""

import pkg_resources,os
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from django.core.files.base import ContentFile
from xblock.fields import Scope, String
from django.template import Context, Template
import logging
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string
from webob import Response


# Make '_' a no-op so we can scrape strings
_ = lambda text: text

log = logging.getLogger(__name__)


@XBlock.wants("settings")
class JupterLiteXBlock(XBlock):
    """
       EdX XBlock for embedding JupyterLite, allowing learners to interact with Jupyter notebooks.
       Instructors can configure JupyterLite settings in Studio, and learners access notebooks in the LMS 
    """


    jupyterlite_url = String(
        display_name=_("JupyterLite Service URL"),
        help="The URL of the JupyterLite service",
        scope=Scope.settings,
        default="http://jupyterlite.local.overhang.io:9500/lab/index.html"
    )
    default_notebook = String(
        display_name=_("Default Notebook"),
        scope=Scope.content,
        help=_("The default notebook for the JupyterLite service"),
        default=""
    )
    display_name = String(
        display_name=_("JupyterLite"),
        help=_("Display name for this module"),
        default="JupyterLite Notebook",
        scope=Scope.settings
    )
    viewed_by_learner = String(
        display_name=_("Saved Notebook URLs"),
        default="",
        scope=Scope.user_state,
        help="List of notebook URLs saved by the learner."
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

            def get_default_storage(_xblock, bucket_name):
                return default_storage

            storage_func = self.xblock_settings.get("STORAGE_FUNC", get_default_storage)
            if isinstance(storage_func, str):
                storage_func = import_string(storage_func)
            bucket_name = self.xblock_settings.get("S3_BUCKET_NAME", None)
            self._storage = storage_func(self, bucket_name)

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
        file_name = os.path.basename(self.default_notebook) if self.default_notebook else ''
        url = self.jupyterlite_url
        if file_name not in self.viewed_by_learner.split(','):
            self.viewed_by_learner += ',' + file_name
            url += f'?fromURL={self.default_notebook}'
        else:
            url += f'?path={file_name}'
            
        jupyterlite_iframe = '<iframe src="{}" width="100%" height="600px" style="border: none;"></iframe>'.format(url)
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
    
    def delete_existing_files(self):
        """
        Delete existing files in the notebook folder.
        """
        folder_path = self.folder_base_path
        if not self.storage.exists(folder_path):
            return
        
        existing_files = self.storage.listdir(folder_path)[1]
        for filename in existing_files:
            file_path = f"{folder_path}/{filename}"
            self.storage.delete(file_path)
    
    def save_file(self, uploaded_file):
        self.delete_existing_files()
        path = self.storage.save(f'{self.folder_base_path}/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        url = self.storage.url(path)
        if url.startswith(('http://', 'https://')):
            uploaded_file_url = url
        else:
            scheme = "https" if settings.HTTPS == "on" else "http"
            root_url = f'{scheme}://{settings.CMS_BASE}'
            uploaded_file_url = root_url+url
            
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

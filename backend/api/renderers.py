import io

from rest_framework import renderers


class DownloadRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        text_buffer = io.StringIO()
        text_buffer.write("--- Список ингредиентов для покупки ---\n")
        for d in data:
            text_buffer.write(
                str(dict(d).get("ingredient_name"))
                + " "
                + str(dict(d).get("total_amount"))
                + " "
                + str(dict(d).get("measurement_unit"))
                + "\n"
            )
        return text_buffer.getvalue()

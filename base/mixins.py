class SuccessMessageMixin:
    """
    Adds a resource name and success message to the renderer context to be used by
    a renderer to display success messages.
    """
    resource_name = None
    success_message = None

    def get_renderer_context(self):
        context = super().get_renderer_context()

        if not self.resource_name:
            try:
                self.resource_name = type(self.get_queryset()[0]).__name__ if hasattr(
                    self, 'get_queryset') else None
            except IndexError as e:
                # If the queryset returns an empty list,
                # set `success_message` to 'No records found.'
                self.success_message = 'No records found.'
            except:
                # If an error is raised, fail silently and move on.
                pass

        context['resource_name'] = self.resource_name
        context['success_message'] = self.success_message

        return context

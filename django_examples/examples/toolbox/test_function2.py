from toolbox_view import ToolBoxBase


class DemoFile2(ToolBoxBase):
    button_text = 'Another file'
    button_group = 'Named Group'
    button_colour = 'danger'

    def button_function(self):
        return self.command_response('message', text='Another File')

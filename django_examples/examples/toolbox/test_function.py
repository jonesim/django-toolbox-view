from time import sleep

from ajax_helpers.utils import ajax_command

from toolbox_view import ToolBoxBase
from toolbox_view.modal_confirm import ConfirmToolbox
from toolbox_view.report import ReportFile


class DemoToolbox(ToolBoxBase):
    button_text = 'Test'
    tooltip = 'Asks for confirmation, then shows a message'

    @ConfirmToolbox(message='Please confirm')
    def button_function(self):
        return self.command_response('message', text='Completed')


class DemoToolbox1(ToolBoxBase):
    button_text = 'Task Test'
    button_colour = 'danger'
    task = True

    @ConfirmToolbox(message='Run the demo task? It takes about 5 seconds.')
    def button_function(self):
        self.update_message('Starting demo task ')
        for a in range(1, 6):
            sleep(1)
            self.update_message(f'Demo task {a} seconds')
        return [ajax_command('message', text='Completed Task')]


class ReportToolbox(ToolBoxBase):
    button_text = 'Produce Report'

    def button_function(self):
        self.report = ReportFile('test.csv', folder='')
        self.report.write_csv_line(['test1', 'test2'])
        return self.command_response('message', text='Report produced')

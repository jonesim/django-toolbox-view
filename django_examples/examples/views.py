from django_menus.menu import AjaxMenuTabs, MenuItem

from toolbox_view.views import Toolbox


class TabToolboxView(AjaxMenuTabs, Toolbox):

    template_name = 'base_template.html'
    tab_template = 'tab_template.html'
    menu_display = 'Subclassed View'

    def setup_menu(self):
        self.add_menu('main_menu').add_items('subclassed_view',  MenuItem('toolbox:toolbox', 'Simple View'))

    def test_func(self):
        return True

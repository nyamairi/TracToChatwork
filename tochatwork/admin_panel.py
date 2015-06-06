import pkg_resources

from trac.core import Component, implements
from trac.admin import IAdminPanelProvider
from trac.web.chrome import add_notice, add_warning, ITemplateProvider
from trac.util.text import exception_to_unicode

SECTION_NAME = 'tochatwork'


class AdminPanel(Component):
    implements(IAdminPanelProvider, ITemplateProvider)

    def get_admin_panels(self, req):
        if 'TRAC_ADMIN' in req.perm:
            yield ('tochatwork', 'ToChatwork', 'settings', 'Settings')

    def render_admin_panel(self, req, cat, page, version):
        self.log.debug("cat: %s page: %s", cat, page)
        req.perm.require('TRAC_ADMIN')

        options = (
            'api_base_url',
            'api_token',
            'room_id',
            'only_owner_changed',
            'notify_symbol',
            'api_token_field_name')

        self.log.debug("method: %s", req.method)
        if req.method == 'POST':
            for option in options:
                self.config.set(SECTION_NAME, option, req.args.get(option))

            try:
                self.config.save()
                self.log.debug('config saved.')
                add_notice(req, 'Your changes have been saved.')
            except Exception, e:
                self.log.error("Error writing to trac.ini: %s", exception_to_unicode(e))
                add_warning(req, 'Error writing to trac.ini.')

            req.redirect(req.href.admin(cat, page))

        params = dict([(option, self.config.get(SECTION_NAME, option)) for option in options])
        return 'settings.html', params

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('tochatwork', 'templates')]
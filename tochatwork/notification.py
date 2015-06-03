import sys
import requests

from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener
from trac.wiki.model import WikiPage


CONFIG_SECTION = 'tochatwork'


class NotificationPlugin(Component):
    implements(ITicketChangeListener)

    def ticket_created(self, ticket):
        self._post_info(ticket, """チケットが登録されました 報告者: {reporter} 担当者: {owner}

{description}""".format(reporter=ticket['reporter'], owner=ticket['owner'], description=ticket['description']))

    def ticket_changed(self, ticket, comment, author, old_values):
        if not self._should_notify(ticket, comment, author, old_values):
            return

        self._post_info(ticket, """チケットが更新されました 更新者: {author} 担当者: {owner} ステータス: {status}

{comment}""".format(author=author, owner=ticket['owner'], comment=comment, status=ticket['status']))

    def ticket_deleted(self, ticket):
        pass

    def ticket_comment_modified(self, ticket, cdate, author, comment, old_comment):
        self._post_info(ticket, """チケットのコメントが更新されました 更新者: {author} 担当者: {owner}

{comment}""".format(author=author, owner=ticket['owner'], comment=comment))

    def ticket_change_deleted(self, ticket, cdate, changes):
        pass

    def _should_notify(self, ticket, comment, author, old_values):
        if comment == '':
            return False

        notify_symbol = self._get_notify_symbol()
        if notify_symbol != '' and notify_symbol in comment:
            return True

        if self._only_owner_changed() and 'owner' not in old_values:
            return False

        return True

    def _get_notify_symbol(self):
        return self._get_config('notify_symbol')

    def _only_owner_changed(self):
        return self._get_bool_config('only_owner_changed')

    def _post_info(self, ticket, body):
        trac_base_url = self.config.get('trac', 'base_url')
        self.log.debug("trac_base_url: %s", trac_base_url)
        self._post_message("[info][title]#{id} {summary}[/title]{body}\n\n{trac_base_url}/ticket/{id}[/info]".format(
            id=ticket.id,
            summary=ticket['summary'],
            body=body,
            trac_base_url=trac_base_url))

    def _post_message(self, message):
        api_base_url = self._get_config('api_base_url')
        self.log.debug("api_base_url: %s", api_base_url)
        api_token = self._get_config('api_token')
        self.log.debug("api_token: %s", api_token)
        room_id = self._get_config('room_id')
        self.log.debug("room_id: %s", room_id)
        res = requests.post(
            "{api_base_url}/rooms/{room_id}/messages".format(api_base_url=api_base_url, room_id=room_id),
            data={'body': message},
            headers={'X-ChatWorkToken': api_token})
        self.log.debug("response: %s", res.text)

    def _get_config(self, key):
        return self.config.get(CONFIG_SECTION, key)

    def _get_bool_config(self, key, default=''):
        return self.config.getbool(CONFIG_SECTION, key, default)
import sys
import requests

from trac.core import Component, implements
from trac.ticket.api import ITicketChangeListener
from trac.wiki.model import WikiPage


CONFIG_SECTION = 'tochatwork'


class NotificationPlugin(Component):
    implements(ITicketChangeListener)

    def ticket_created(self, ticket):
        body = """チケットが登録されました 報告者: {reporter} 担当者: {owner}

{description}""".format(reporter=ticket['reporter'], owner=ticket['owner'], description=ticket['description'])

        self._post_info(ticket['reporter'], ticket, body, to=ticket['owner'])

    def ticket_changed(self, ticket, comment, author, old_values):
        if not self._should_notify(ticket, comment, author, old_values):
            return

        body = """チケットが更新されました 更新者: {author} 担当者: {owner} ステータス: {status}

{comment}""".format(author=author, owner=ticket['owner'], comment=comment, status=ticket['status'])

        to = ''
        if author != ticket['owner']:
            to = ticket['owner']

        self._post_info(author, ticket, body, to=to)

    def ticket_deleted(self, ticket):
        pass

    def ticket_comment_modified(self, ticket, cdate, author, comment, old_comment):
        body = """チケットのコメントが更新されました 更新者: {author} 担当者: {owner}

{comment}""".format(author=author, owner=ticket['owner'], comment=comment)
        self._post_info(author, ticket, body)

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

    def _build_info_message(self, body, ticket):
        trac_base_url = self.config.get('trac', 'base_url')
        self.log.debug("trac_base_url: %s", trac_base_url)
        return "[info][title]#{id} {summary}[/title]{body}\n\n{trac_base_url}/ticket/{id}[/info]".format(
            id=ticket.id, summary=ticket['summary'], body=body, trac_base_url=trac_base_url)

    def _get_account(self, api_token):
        api_base_url = self._get_config('api_base_url')
        self.log.debug("api_base_url: %s", api_base_url)

        res = requests.get("{api_base_url}/me".format(api_base_url=api_base_url),
                           headers={'X-ChatWorkToken': api_token})
        self.log.debug("response: %s", res.text)

        return res.json()

    def _request_account(self, to):
        api_token = self._get_api_token(to)
        if api_token == '':
            return None

        return self._get_account(api_token)

    def _build_to_message(self, params):
        account = self._request_account(params.get('to', ''))
        if account is None:
            return ''

        return "[To:{account_id}]{name}さん\n".format(account_id=account['account_id'], name=account['name'])

    def _post_info(self, contributor, ticket, body, **params):
        message = self._build_to_message(params) + self._build_info_message(body, ticket)
        self._post_message(contributor, message)

    def _post_message(self, contributor, message):
        api_base_url = self._get_config('api_base_url')
        self.log.debug("api_base_url: %s", api_base_url)
        api_token = self._get_contributor_api_token(contributor)
        self.log.debug("api_token: %s", api_token)
        room_id = self._get_config('room_id')
        self.log.debug("room_id: %s", room_id)
        res = requests.post(
            "{api_base_url}/rooms/{room_id}/messages".format(api_base_url=api_base_url, room_id=room_id),
            data={'body': message},
            headers={'X-ChatWorkToken': api_token})
        self.log.debug("response: %s", res.text)

    def _get_api_token(self, session_id):
        self.log.debug("session_id: %s", session_id)

        field_name = self._get_config('api_token_field_name', '')
        self.log.debug("field_name: %s", field_name)
        if field_name == '':
            return ''

        with self.env.get_read_db() as db:
            for row in db.execute(
                    "SELECT value FROM session_attribute WHERE sid = :session_id AND name = :field_name",
                    {'session_id': session_id, 'field_name': field_name}):
                token, = row
                self.log.debug("chatwork_api_token: %s", token)
                if token != '':
                    return token

        return ''

    def _get_contributor_api_token(self, session_id):
        api_token = self._get_api_token(session_id)
        if api_token != '':
            return api_token

        return self._get_config('api_token')

    def _get_config(self, key, default=''):
        return self.config.get(CONFIG_SECTION, key, default)

    def _get_bool_config(self, key, default=''):
        return self.config.getbool(CONFIG_SECTION, key, default)
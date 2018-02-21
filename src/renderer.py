import logging
import re
from urllib.parse import unquote

import troposphere

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class NotMatchError(Exception):
    ...


class Type(object):

    name = None
    pattern = None

    @property
    def split_exp(self):
        return '{}\({}\)'.format(self.name, self.pattern)

    @property
    def match_exp(self):
        return '^{}\(({})\)$'.format(self.name, self.pattern)

    def _handle(self, value):
        return getattr(troposphere, self.name)(unquote(value))

    def do(self, value):
        try:
            return self._handle(re.match(self.match_exp, value).group(1))
        except AttributeError as e:
            raise NotMatchError(e.args)


class Ref(Type):

    name = 'Ref'
    pattern = '[a-zA-Z0-9\-:%]+'


class GetAtt(Type):

    name = 'GetAtt'
    pattern = '[a-zA-Z0-9, \-:%]+'

    def _handle(self, value):
        return getattr(troposphere, self.name)(*[unquote(k.strip()) for k in value.split(',') if k.strip()])


SUPPORTED_ELEMENTS = (
    Ref(),
    GetAtt(),
)


def to_userdata(userdata_str, base64_encode=True):
    splitted = re.split('(%s)' % ('|'.join(map(lambda e: e.split_exp, SUPPORTED_ELEMENTS))), userdata_str)

    def check(value):
        for e in SUPPORTED_ELEMENTS:
            try:
                return e.do(value)
            except NotMatchError:
                ...
        return value

    userdata = troposphere.Join('', list(map(check, splitted)))
    return troposphere.Base64(userdata) if base64_encode else userdata

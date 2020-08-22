from envparse import env


env.read_envfile()

API_ID = env.int('API_ID')
API_HASH = env.str('API_HASH')

USER_PHONE = env.str('USER_PHONE')

GITHUB_LINK = 'https://github.com/WhiteMemory99/telecharm-userbot'
GUIDE_LINK_RU = 'https://telegra.ph/Telecharm-prodvinutye-komandy-08-19'
GUIDE_LINK_EN = 'https://telegra.ph/Telecharm-advanced-commands-08-19'
TELECHARM_VERSION = '0.2.1'

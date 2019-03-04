import base64
import datetime
from cryptoauthlib import *
from cryptoauthlib import PyJWT

AUTH_LIB_INITIATED = False
ATCA_SUCCESS = 0x00
cfg = cfg_ateccx08a_i2c_default()

def auth_lib_init():
    load_cryptoauthlib()
    cfg.cfg.atcai2c.bus = 1
    assert atcab_init(cfg) == ATCA_SUCCESS
    AUTH_LIB_INITIATED = True

def generate_token(project_id):
    if not AUTH_LIB_INITIATED:
        auth_lib_init()

    public_key = get_public_key()

    claims = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }

    token = PyJWT(0, cfg)
    return token.encode(claims, public_key, algorithm='ES256')

def get_public_key():
    public_key = bytearray(64)
    assert atcab_get_pubkey(0, public_key) == ATCA_SUCCESS

    public_key_pem = bytearray.fromhex('3059301306072A8648CE3D020106082A8648CE3D03010703420004') + public_key
    public_key_pem = '-----BEGIN PUBLIC KEY-----\n' + base64.b64encode(public_key_pem).decode('ascii') + '\n-----END PUBLIC KEY-----'

    return public_key_pem

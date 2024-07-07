import configparser
from typing import Dict
from conf import CFG_DIR


def _load_cfg():
    cfg = configparser.ConfigParser()
    cfg.read(f'{CFG_DIR}conf.cfg')
    return cfg


def get_smtp_conf(
        config: configparser.ConfigParser,
        gen_smtp: str) -> Dict[str, str|int]:
    smtp_setting = gen_smtp.upper()
    smpt_setting_section = f"SMTP.{smtp_setting}"
    host = config.get(smpt_setting_section, "HOST")
    port = int(config.get(smpt_setting_section, "PORT"))
    user = config.get(smpt_setting_section, "USER")
    pswd = config.get(smpt_setting_section, "PASS")
    send_as = config.get(smpt_setting_section, "SEND_AS")
    return {
        "HOST": host,
        "PORT": port,
        "USER": user,
        "PASS": pswd,
        "SEND_AS": send_as
    }


def get_data_conf(
        config: configparser.ConfigParser, gen_data: str) -> Dict[str, str|int]:
    data_setting = gen_data.upper()
    data_setting_section = f"DB.{data_setting}"
    host = config.get(data_setting_section, "HOST")
    port = int(config.get(data_setting_section, "PORT"))
    user = config.get(data_setting_section, "USER")
    pswd = config.get(data_setting_section, "PASS")
    name = config.get(data_setting_section, "NAME")
    return {
        "HOST": host,
        "PORT": port,
        "USER": user,
        "PASS": pswd,
        "NAME": name
    }

def get_cfg_params():
    cfg = _load_cfg()
    gen_smtp = cfg.get("GEN", "SMTP")
    gen_data = cfg.get("GEN", "DATA")
    return gen_smtp, gen_data


def get_cfg():
    gen_smtp, gen_data = get_cfg_params()

    cfg = _load_cfg()
    smtp = get_smtp_conf(cfg, gen_smtp)
    data = get_data_conf(cfg, gen_data)
    return {
        "SMTP": smtp,
        "DATA": data
    }

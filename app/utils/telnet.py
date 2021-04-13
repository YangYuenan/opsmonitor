# -*- coding: utf-8 -*-
import telnetlib


def telnet(ip, port=23, timeout=10):
    tn = telnetlib.Telnet()
    try:
        tn.open(host=ip, port=port, timeout=timeout)
        return
    except Exception as e:
        return str(e)
    finally:
        tn.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from z3 import *
from attacks.abstract_attack import AbstractAttack
from gmpy2 import isqrt
from lib.utils import timeout, TimeoutError
from lib.keys_wrapper import PrivateKey


class Attack(AbstractAttack):
    def __init__(self, attack_rsa_obj, timeout=60):
        super().__init__(attack_rsa_obj, timeout)
        self.speed = AbstractAttack.speed_enum["medium"]

    def z3_solve(self, n, timeout_amount):
        p = Int("x")
        q = Int("y")
        s = Solver()
        i = int(isqrt(n))
        s.add(p * q == n, p > 1, q > i, q > p)
        s.set("timeout", timeout_amount * 1000)
        try:
            s_check_output = s.check()
            print(s_check_output)
            res = s.model()
            return res[p], res[q]
        except:
            return None, None

    def attack(self, publickey, cipher=[]):

        if not hasattr(publickey, "p"):
            publickey.p = None
        if not hasattr(publickey, "q"):
            publickey.q = None

        # solve with z3 theorem prover
        with timeout(self.timeout):
            try:
                try:
                    euler_res = self.z3_solve(publickey.n, timeout_amount)
                except:
                    self.logger.warning("[!] z3: Internal Error.")
                    return (None, None)

                if euler_res and len(euler_res) > 1:
                    publickey.p, publickey.q = euler_res

                if publickey.q is not None:
                    priv_key = PrivateKey(
                        int(publickey.p),
                        int(publickey.q),
                        int(publickey.e),
                        int(publickey.n),
                    )
                    return (priv_key, None)
            except TimeoutError:
                return (None, None)

        return (None, None)


if __name__ == "__main__":
    attack = Attack()
    attack.test()
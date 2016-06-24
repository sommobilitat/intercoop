# -*- encoding: utf-8 -*-

import unittest
import intercoop
import os
from yamlns import namespace as ns


class IntercoopMessage_Test(unittest.TestCase):

    payload1=u"""\
intercoopVersion: '1.0'
originpeer: testpeer
origincode: 666
name: Perico de los Palotes
address: Percebe, 13
city: Villarriba del Alcornoque
state: Albacete
postalcode: '01001'
country: ES
"""
    def setUp(self):
        self.maxDiff = None
        self.keyfile = 'testkey.pem'
        if not os.access(self.keyfile, os.F_OK):
            self.key = intercoop.generateKeyPair(self.keyfile)
        self.key = intercoop.loadKeyPair(self.keyfile)

        self.values = ns.loads(self.payload1)
        self.encodedPayload1 = intercoop.encode(self.payload1)
        self.signedPayload1 = intercoop.sign(self.key, self.payload1)

    def test_produce(self):
        g = intercoop.Generator(ownKeyPair = self.key)
        message = g.produce(self.values)
        self.assertEqual(
            dict(ns.loads(message)),
            dict(
                intercoopVersion = '1.0',
                signature = self.signedPayload1,
                payload = self.encodedPayload1,
            ))

    def test_parse(self):
        message = ns(
            intercoopVersion = '1.0',
            signature = self.signedPayload1,
            payload = self.encodedPayload1,
            ).dump()

        g = intercoop.Parser(ownKeyPair = self.key)
        values = g.parse(message)
        self.assertEqual(
            dict(self.values),
            dict(values),
            )

    class KeyRingMock(object):
        def __init__(self, keys):
            self.keys = keys
        def get(self, key):
            return self.keys[key]

    def test_parse_withInvalidSignature(self):
        message = ns(
            intercoopVersion = '1.0',
            signature = intercoop.sign(self.key, self.payload1+"\n"),
            payload = self.encodedPayload1,
            ).dump()

        g = intercoop.Parser(ownKeyPair = self.key)
        with self.assertRaises(intercoop.BadSignature) as ctx:
            g.parse(message)
        self.assertEqual(ctx.exception.args[0],
            "Signature didn't match the content, content modified")
            

unittest.TestCase.__str__ = unittest.TestCase.id



if __name__ == "__main__":
    import sys
    unittest.main()


# vim: ts=4 sw=4 et
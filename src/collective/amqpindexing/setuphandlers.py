# -*- coding: utf-8 -*-


def testSetup(context):
    if context.readDataFile('collective.amqpindexing.txt') is None:
        return

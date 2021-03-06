# SPDX-License-Identifier: (GPL-2.0 OR Linux-OpenIB)
# Copyright (c) 2019 Mellanox Technologies, Inc. All rights reserved. See COPYING file
# Copyright (c) 2020 Kamal Heib <kamalheib1@gmail.com>, All rights reserved.  See COPYING file

"""
Test module for pyverbs' qp module.
"""
import unittest
import random
import errno
import os

from pyverbs.pyverbs_error import PyverbsRDMAError
from pyverbs.qp import QPInitAttr, QPAttr, QP
from tests.base import PyverbsAPITestCase
import pyverbs.utils as pu
import pyverbs.enums as e
from pyverbs.pd import PD
from pyverbs.cq import CQ
import tests.utils as u


class QPTest(PyverbsAPITestCase):
    """
    Test various functionalities of the QP class.
    """

    def create_qp(self, creator, qp_init_attr, is_ex, with_attr):
        """
        Auxiliary function to create QP object.
        """
        try:
            qp_attr = (None, QPAttr())[with_attr]
            return QP(creator, qp_init_attr, qp_attr)
        except PyverbsRDMAError as ex:
            if ex.error_code == errno.EOPNOTSUPP:
                with_str = ('without', 'with')[with_attr] + ('', ' extended')[is_ex]
                qp_type_str = pu.qp_type_to_str(qp_init_attr.qp_type)
                raise unittest.SkipTest(f'Create {qp_type_str} QP {with_str} attrs is not supported')
            raise ex

    def create_qp_common_test(self, qp_type, qp_state, is_ex, with_attr):
        """
        Common function used by create QP tests.
        """
        for ctx, attr, attr_ex in self.devices:
            with PD(ctx) as pd:
                with CQ(ctx, 100, None, None, 0) as cq:
                    if qp_type == e.IBV_QPT_RAW_PACKET:
                        eth_port = 0
                        for i in range(1, attr.phys_port_cnt + 1):
                            if u.is_eth(ctx, i) and u.is_root():
                                eth_port = i
                                break
                        if eth_port == 0:
                            raise unittest.SkipTest('To Create RAW QP must be done by root on Ethernet link layer')

                    if is_ex:
                        qia = get_qp_init_attr_ex(cq, pd, attr, attr_ex, qp_type)
                        creator = ctx
                    else:
                        qia = get_qp_init_attr(cq, attr)
                        qia.qp_type = qp_type
                        creator = pd

                    qp = self.create_qp(creator, qia, is_ex, with_attr)
                    qp_type_str = pu.qp_type_to_str(qp_type)
                    qp_state_str = pu.qp_state_to_str(qp_state)
                    assert qp.qp_state == qp_state , f'{qp_type_str} QP should have been in {qp_state_str}'

    def test_create_rc_qp_no_attr(self):
        """
        Test RC QP creation via ibv_create_qp without a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_RC, e.IBV_QPS_RESET, False, False)

    def test_create_uc_qp_no_attr(self):
        """
        Test UC QP creation via ibv_create_qp without a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UC, e.IBV_QPS_RESET, False, False)

    def test_create_ud_qp_no_attr(self):
        """
        Test UD QP creation via ibv_create_qp without a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UD, e.IBV_QPS_RESET, False, False)

    def test_create_raw_qp_no_attr(self):
        """
        Test RAW Packet QP creation via ibv_create_qp without a QPAttr object
        provided.
        Raw Packet is skipped for non-root users / Infiniband link layer.
        """
        self.create_qp_common_test(e.IBV_QPT_RAW_PACKET, e.IBV_QPS_RESET, False, False)

    def test_create_rc_qp_with_attr(self):
        """
        Test RC QP creation via ibv_create_qp with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_RC, e.IBV_QPS_INIT, False, True)

    def test_create_uc_qp_with_attr(self):
        """
        Test UC QP creation via ibv_create_qp with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UC, e.IBV_QPS_INIT, False, True)

    def test_create_ud_qp_with_attr(self):
        """
        Test UD QP creation via ibv_create_qp with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UD, e.IBV_QPS_RTS, False, True)

    def test_create_raw_qp_with_attr(self):
        """
        Test RAW Packet QP creation via ibv_create_qp with a QPAttr object
        provided.
        Raw Packet is skipped for non-root users / Infiniband link layer.
        """
        self.create_qp_common_test(e.IBV_QPT_RAW_PACKET, e.IBV_QPS_RTS, False, True)

    def test_create_rc_qp_ex_no_attr(self):
        """
        Test RC QP creation via ibv_create_qp_ex without a QPAttr object
        provided.
        """
        self.create_qp_common_test(e.IBV_QPT_RC, e.IBV_QPS_RESET, True, False)

    def test_create_uc_qp_ex_no_attr(self):
        """
        Test UC QP creation via ibv_create_qp_ex without a QPAttr object
        provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UC, e.IBV_QPS_RESET, True, False)

    def test_create_ud_qp_ex_no_attr(self):
        """
        Test UD QP creation via ibv_create_qp_ex without a QPAttr object
        provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UD, e.IBV_QPS_RESET, True, False)

    def test_create_raw_qp_ex_no_attr(self):
        """
        Test Raw Packet QP creation via ibv_create_qp_ex without a QPAttr object
        provided.
        Raw Packet is skipped for non-root users / Infiniband link layer.
        """
        self.create_qp_common_test(e.IBV_QPT_RAW_PACKET, e.IBV_QPS_RESET, True, False)

    def test_create_rc_qp_ex_with_attr(self):
        """
        Test RC QP creation via ibv_create_qp_ex with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_RC, e.IBV_QPS_INIT, True, True)

    def test_create_uc_qp_ex_with_attr(self):
        """
        Test UC QP creation via ibv_create_qp_ex with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UC, e.IBV_QPS_INIT, True, True)

    def test_create_ud_qp_ex_with_attr(self):
        """
        Test UD QP creation via ibv_create_qp_ex with a QPAttr object provided.
        """
        self.create_qp_common_test(e.IBV_QPT_UD, e.IBV_QPS_RTS, True, True)

    def test_create_raw_qp_ex_with_attr(self):
        """
        Test Raw Packet QP creation via ibv_create_qp_ex with a QPAttr object
        provided.
        Raw Packet is skipped for non-root users / Infiniband link layer.
        """
        self.create_qp_common_test(e.IBV_QPT_RAW_PACKET, e.IBV_QPS_RTS, True, True)

    def verify_qp_attrs(self, orig_cap, state, init_attr, attr):
        self.assertEqual(state, attr.cur_qp_state)
        self.assertLessEqual(orig_cap.max_send_wr, init_attr.cap.max_send_wr)
        self.assertLessEqual(orig_cap.max_recv_wr, init_attr.cap.max_recv_wr)
        self.assertLessEqual(orig_cap.max_send_sge, init_attr.cap.max_send_sge)
        self.assertLessEqual(orig_cap.max_recv_sge, init_attr.cap.max_recv_sge)
        self.assertLessEqual(orig_cap.max_inline_data, init_attr.cap.max_inline_data)

    def query_qp_common_test(self, qp_type):
        for ctx, attr, attr_ex in self.devices:
            with PD(ctx) as pd:
                with CQ(ctx, 100, None, None, 0) as cq:
                    if qp_type == e.IBV_QPT_RAW_PACKET:
                        eth_port = 0
                        for i in range(1, attr.phys_port_cnt + 1):
                            if u.is_eth(ctx, i) and u.is_root():
                                eth_port = i
                                break
                        if eth_port == 0:
                            raise unittest.SkipTest('To Create RAW QP must be done by root on Ethernet link layer')

                    # Legacy QP
                    qia = get_qp_init_attr(cq, attr)
                    qia.qp_type = qp_type
                    caps = qia.cap
                    qp = self.create_qp(pd, qia, False, False)
                    qp_attr, qp_init_attr = qp.query(e.IBV_QP_STATE | e.IBV_QP_CAP)
                    self.verify_qp_attrs(caps, e.IBV_QPS_RESET, qp_init_attr, qp_attr)

                    # Extended QP
                    qia = get_qp_init_attr_ex(cq, pd, attr, attr_ex, qp_type)
                    caps = qia.cap # Save them to verify values later
                    qp = self.create_qp(ctx, qia, True, False)
                    qp_attr, qp_init_attr = qp.query(e.IBV_QP_STATE | e.IBV_QP_CAP)
                    self.verify_qp_attrs(caps, e.IBV_QPS_RESET, qp_init_attr, qp_attr)

    def test_query_rc_qp(self):
        """
        Queries an RC QP after creation. Verifies that its properties are as
        expected.
        """
        self.query_qp_common_test(e.IBV_QPT_RC)

    def test_query_uc_qp(self):
        """
        Queries an UC QP after creation. Verifies that its properties are as
        expected.
        """
        self.query_qp_common_test(e.IBV_QPT_UC)

    def test_query_ud_qp(self):
        """
        Queries an UD QP after creation. Verifies that its properties are as
        expected.
        """
        self.query_qp_common_test(e.IBV_QPT_UD)

    def test_query_raw_qp(self):
        """
        Queries an RAW Packet QP after creation. Verifies that its properties
        are as expected.
        Raw Packet is skipped for non-root users / Infiniband link layer.
        """
        self.query_qp_common_test(e.IBV_QPT_RAW_PACKET)

    def test_modify_ud_qp(self):
        """
        Queries a UD QP after calling modify(). Verifies that its properties are
        as expected.
        """
        for ctx, attr, attr_ex in self.devices:
            with PD(ctx) as pd:
                with CQ(ctx, 100, None, None, 0) as cq:
                    # Legacy QP
                    qia = get_qp_init_attr(cq, attr)
                    qia.qp_type = e.IBV_QPT_UD
                    qp = self.create_qp(pd, qia, False, False)
                    qa = QPAttr()
                    qa.qkey = 0x123
                    qp.to_init(qa)
                    qp_attr, _ = qp.query(e.IBV_QP_QKEY)
                    assert qp_attr.qkey == qa.qkey, 'Legacy QP, QKey is not as expected'
                    qp.to_rtr(qa)
                    qa.sq_psn = 0x45
                    qp.to_rts(qa)
                    qp_attr, _ = qp.query(e.IBV_QP_SQ_PSN)
                    assert qp_attr.sq_psn == qa.sq_psn, 'Legacy QP, SQ PSN is not as expected'
                    qa.qp_state = e.IBV_QPS_RESET
                    qp.modify(qa, e.IBV_QP_STATE)
                    assert qp.qp_state == e.IBV_QPS_RESET, 'Legacy QP, QP state is not as expected'
                    # Extended QP
                    qia = get_qp_init_attr_ex(cq, pd, attr, attr_ex, e.IBV_QPT_UD)
                    qp = self.create_qp(ctx, qia, True, False)
                    qa = QPAttr()
                    qa.qkey = 0x123
                    qp.to_init(qa)
                    qp_attr, _ = qp.query(e.IBV_QP_QKEY)
                    assert qp_attr.qkey == qa.qkey, 'Extended QP, QKey is not as expected'
                    qp.to_rtr(qa)
                    qa.sq_psn = 0x45
                    qp.to_rts(qa)
                    qp_attr, _ = qp.query(e.IBV_QP_SQ_PSN)
                    assert qp_attr.sq_psn == qa.sq_psn, 'Extended QP, SQ PSN is not as expected'
                    qa.qp_state = e.IBV_QPS_RESET
                    qp.modify(qa, e.IBV_QP_STATE)
                    assert qp.qp_state == e.IBV_QPS_RESET, 'Extended QP, QP state is not as expected'


def get_qp_init_attr(cq, attr):
    """
    Creates a QPInitAttr object with a QP type of the provided <qpts> array and
    other random values.
    :param cq: CQ to be used as send and receive CQ
    :param attr: Device attributes for capability checks
    :return: An initialized QPInitAttr object
    """
    qp_cap = u.random_qp_cap(attr)
    sig = random.randint(0, 1)
    return QPInitAttr(scq=cq, rcq=cq, cap=qp_cap, sq_sig_all=sig)


def get_qp_init_attr_ex(cq, pd, attr, attr_ex, qpt):
    """
    Creates a QPInitAttrEx object with a QP type of the provided <qpts> array
    and other random values.
    :param cq: CQ to be used as send and receive CQ
    :param pd: A PD object to use
    :param attr: Device attributes for capability checks
    :param attr_ex: Extended device attributes for capability checks
    :param qpt: QP type
    :return: An initialized QPInitAttrEx object
    """
    qia = u.random_qp_init_attr_ex(attr_ex, attr, qpt)
    qia.send_cq = cq
    qia.recv_cq = cq
    qia.pd = pd  # Only XRCD can be created without a PD
    return qia

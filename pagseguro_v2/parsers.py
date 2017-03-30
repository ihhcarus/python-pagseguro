# -*- coding: utf-8 -*-


import logging

import xmltodict

from .config import Config
from .utils import parse_date


logger = logging.getLogger()


class XMLParser(object):
    def __init__(self, xml, config=None):
        self.xml = xml
        self.errors = None
        if config is None:
            config = Config()
        self.config = config
        self.parse_xml(xml)
        logger.debug(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key, None)

    def parse_xml(self, xml):
        try:
            parsed = xmltodict.parse(xml, encoding="iso-8859-1")
        except Exception as e:
            logger.debug('Cannot parse the returned xml "%s" -> "%s"', xml, e)
            parsed = {}

        if 'errors' in parsed:
            self.errors = parsed['errors']['error']

        return parsed


class PagSeguroNotificationResponse(XMLParser):
    def parse_xml(self, xml):
        parsed = super(PagSeguroNotificationResponse, self).parse_xml(xml)
        if self.errors:
            return
        transaction = parsed.get('transaction', {})
        for k, v in transaction.items():
            setattr(self, k, v)


class PagSeguroCheckoutSession(XMLParser):
    def __init__(self, xml, config=None):
        self.session_id = None
        super(PagSeguroCheckoutSession, self).__init__(xml, config)

    def parse_xml(self, xml):
        parsed = super(PagSeguroCheckoutSession, self).parse_xml(xml)
        if self.errors:
            return
        session = parsed.get('session', {})
        self.session_id = session.get('id')


class PagSeguroCheckoutResponse(XMLParser):
    code = None
    date = None
    payment_url = None
    payment_link = None
    transaction = None

    def parse_xml(self, xml):
        parsed = super(PagSeguroCheckoutResponse, self).parse_xml(xml)
        if self.errors:
            return
        checkout = parsed.get('checkout', {})
        self.code = checkout.get('code')
        self.date = parse_date(checkout.get('date'))
        self.payment_url = self.config.PAYMENT_URL % self.code
        # this is used only for transparent checkout process
        self.transaction = parsed.get('transaction', {})
        self.payment_link = self.transaction.get('paymentLink')


class PagSeguroTransactionSearchResult(XMLParser):
    current_page = None
    total_pages = None
    results_in_page = None
    transactions = []

    def parse_xml(self, xml):
        parsed = super(PagSeguroTransactionSearchResult, self).parse_xml(xml)
        if self.errors:
            return
        search_result = parsed.get('transactionSearchResult', {})
        self.transactions = search_result.get('transactions', {})
        self.transactions = self.transactions.get('transaction', [])
        if not isinstance(self.transactions, list):
            self.transactions = [self.transactions]
        self.current_page = search_result.get('currentPage', None)
        if self.current_page is not None:
            self.current_page = int(self.current_page)
        self.results_in_page = search_result.get('resultsInThisPage', None)
        if self.results_in_page is not None:
            self.results_in_page = int(self.results_in_page)
        self.total_pages = search_result.get('totalPages', None)
        if self.total_pages is not None:
            self.total_pages = int(self.total_pages)


class PagSeguroPreApproval(XMLParser):
    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApproval, self).parse_xml(xml)
        if self.errors:
            return
        result = parsed.get('preApproval', {})
        self.name = result.get('name', None)
        self.code = result.get('code', None)
        self.date = parse_date(result.get('date'))
        self.tracker = result.get('tracker', None)
        self.status = result.get('status', None)
        self.reference = result.get('reference', None)
        self.last_event_date = result.get('lastEventDate', None)
        self.charge = result.get('charge', None)
        self.sender = result.get('sender', {})


class PagSeguroPreApprovalResponse(XMLParser):
    code = None
    date = None
    payment_url = None
    transaction = None
    payment_link = None

    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApprovalResponse, self).parse_xml(xml)
        if self.errors:
            return
        checkout = parsed.get('preApprovalRequest', {})
        self.code = checkout.get('code')
        self.date = parse_date(checkout.get('date'))
        self.payment_url = self.config.PRE_APPROVAL_PAYMENT_URL % self.code
        # this is used only for transparent checkout process
        self.transaction = parsed.get('transaction', {})
        self.payment_link = self.transaction.get('paymentLink')


class PagSeguroPreApprovalPayment(XMLParser):
    code = None
    date = None

    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApprovalPayment, self).parse_xml(xml)
        if self.errors:
            return
        result = parsed.get('result', {})
        self.code = result.get('transactionCode')
        self.date = parse_date(result.get('date'))


class PagSeguroPreApprovalCancel(XMLParser):
    def __init__(self, request, xml, config=None):
        u""" :type request: requests.models.Response """
        super(PagSeguroPreApprovalCancel, self).__init__(xml, config)
        self.canceled = request.status_code == 204  # no response data so we check the success using the response status code

    def parse_xml(self, xml):
        _ = super(PagSeguroPreApprovalCancel, self).parse_xml(xml)
        if self.errors:
            return


class PagSeguroPreApprovalSearch(XMLParser):
    current_page = None
    total_pages = None
    results_in_page = None
    pre_approvals = []

    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApprovalSearch, self).parse_xml(xml)
        if self.errors:
            return
        search_result = parsed.get('preApprovalSearchResult', {})
        self.pre_approvals = search_result.get('preApprovals', {})
        self.pre_approvals = self.pre_approvals.get('preApproval', [])
        if not isinstance(self.pre_approvals, list):
            self.pre_approvals = [self.pre_approvals]
        self.current_page = search_result.get('currentPage', None)
        if self.current_page is not None:
            self.current_page = int(self.current_page)
        self.results_in_page = search_result.get('resultsInThisPage', None)
        if self.results_in_page is not None:
            self.results_in_page = int(self.results_in_page)
        self.total_pages = search_result.get('totalPages', None)
        if self.total_pages is not None:
            self.total_pages = int(self.total_pages)


class PagSeguroPreApprovalNotificationResponse(XMLParser):
    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApprovalNotificationResponse,
                       self).parse_xml(xml)
        if self.errors:
            return
        transaction = parsed.get('transaction', {})
        for k, v in transaction.items():
            setattr(self, k, v)


class PagSeguroPreApprovalPaymentOrders(XMLParser):
    current_page = None
    total_pages = None
    results_in_page = None
    payment_orders = []

    def parse_xml(self, xml):
        parsed = super(PagSeguroPreApprovalPaymentOrders, self).parse_xml(xml)
        if self.errors:
            return
        search_result = parsed.get('paymentOrdersResult', {})
        self.payment_orders = search_result.get('paymentOrders', {})
        self.payment_orders = self.payment_orders.get('paymentOrder', [])
        if not isinstance(self.payment_orders, list):
            self.payment_orders = [self.payment_orders]
        self.current_page = search_result.get('currentPage', None)
        if self.current_page is not None:
            self.current_page = int(self.current_page)
        self.results_in_page = search_result.get('resultsInThisPage', None)
        if self.results_in_page is not None:
            self.results_in_page = int(self.results_in_page)
        self.total_pages = search_result.get('totalPages', None)
        if self.total_pages is not None:
            self.total_pages = int(self.total_pages)

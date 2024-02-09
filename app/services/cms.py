import json
import random
from typing import Mapping, Any, List, Iterable
from fastapi.logger import logger

import requests
import xmltodict
from pydash import get

from app.services.exceptions import CmsCommunicationFailure, CmsAuthenticationFailure


class CmsClient:
    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.username = username
        self.password = password
        self.session_id = None
        self.logger = logger
        self.login()

        self.ont_slot_table = {
            "OntRg": 8,
            "OntFb": 9,
            "OntEthGe": 3,
            "OntEthFe": 5,
            "OntEthHpna": 4,
            "OntPots": 6,
            "OntDs1": 7,
            "OntRfAvo": None,
            "OntVideoRf": 1,
            "OntVideoHotRf": 2,
        }

    # <------------------------------------------------------------------------------------------------- Authentication

    def login(self):
        """
        # todo make login docs
        :return:
        :raises: CmsAuthenticationFailure if the server responds with an authentication error
        :raises: CmsCommunicationFailure if the request to the server fails
        """
        # Create payload, send it to cms server, and get reply
        payload = self.generate_payload(
            "",
            "auth",
            {"login": {"UserName": self.username, "Password": self.password}},
        )
        resp, _ = self.post(payload, "Envelope.Body.auth-reply")
        resp = resp[0]

        # Extract success code and session id from response, verify the request succeeded
        code = get(resp, "ResultCode")
        session_id = get(resp, "SessionId")

        if session_id is None or code != "0":
            self.logger.critical(
                f"Login request to CMS server at {self.ip} as {self.username} failed with code {code}, message: {None}"  # todo get error message
            )
            raise CmsAuthenticationFailure(self.username, self.ip)

        # Save session id
        self.session_id = session_id

    def logout(self):
        """
        # todo make logout docs
        :return:
        :raises: CmsAuthenticationFailure if the server responds with an authentication error
        :raises: CmsCommunicationFailure if the request to the server fails
        """
        # Create payload, send it to cms server, and get reply
        payload = self.generate_payload(
            "",
            "auth",
            {"logout": {"UserName": self.username, "SessionId": self.session_id}},
        )
        resp, _ = self.post(payload, "Envelope.Body.auth-reply")
        resp = resp[0]

        # Extract success code and session id from response, verify the request succeeded
        code = get(resp, "ResultCode")

        if code != "0":
            self.logger.critical(
                f"Logout request to CMS server at {self.ip} as {self.username} failed with code {code}"
            )
            raise CmsAuthenticationFailure(self.username, self.ip)

        # Clear invalid session id
        self.session_id = None

    # <----------------------------------------------------------------------------------------------------------- Node

    def list_nodes(self):
        pass

    def get_node(self, node_id: str):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {"object": {"type": "System", "id": None}},
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    def get_node_alarms(self, node_id: str):
        """
        todo node alarms docs
        :param node_id:
        :return:
        """
        alarms = []
        action_args = {}
        more = True

        # Repeat request until cms does not declare there's more
        while more:
            payload = self.generate_payload(
                node_id,
                "action",
                {"action-type": "show-alarms", "action-args": action_args},
            )
            resp, more = self.post(
                payload,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.alarm",
            )
            alarms.extend(resp)

            # Assemble after filter
            if more and len(alarms) > 0:
                action_args = {
                    "start-instance": get(alarms[-1], "object"),
                    "after-alarm": get(alarms[-1], "alarm-type"),
                }

        return alarms

    def get_ont_profiles(self, node_id: str):
        pass

    def get_ont_pwe3_profiles(self, node_id: str):
        pass

    # <---------------------------------------------------------------------------------------------------------- Shelf

    def list_node_shelves(self, node_id: str):
        more = True
        shelves = []
        after_filter = {}

        while more:
            # Assemble payload
            action_args = {
                "object": {
                    "type": "System",
                    "id": None,
                    "children": {"type": "Shelf"},
                }
            }
            if after_filter:
                action_args["object"]["children"]["after"] = after_filter

            payload = self.generate_payload(
                node_id,
                "get-config",
                action_args,
            )

            # Send payload and process response
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            shelves.extend(resp)

            # Assemble after filter
            if more and len(resp) > 0:
                after_filter = {
                    "type": get(resp[-1], "type"),
                    "id": get(resp[-1], "id"),
                }

        return shelves

    def get_shelf(self, node_id: str, shelf_nr: int):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {"object": {"type": "Shelf", "id": {"shelf": shelf_nr}}},
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    # <----------------------------------------------------------------------------------------------------------- Card

    def list_shelf_cards(self, node_id: str, shelf_nr: int):
        more = True
        cards = []
        after_filter = {}

        while more:
            # Assemble payload
            action_args = {
                "object": {
                    "type": "Shelf",
                    "id": {
                        "shelf": shelf_nr,
                    },
                    "children": {"type": "Card"},
                }
            }
            if after_filter:
                action_args["object"]["children"]["after"] = after_filter

            payload = self.generate_payload(
                node_id,
                "get-config",
                action_args,
            )

            # Send payload and process response
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            cards.extend(resp)

            # Assemble after filter
            if more and len(resp) > 0:
                after_filter = {
                    "type": get(resp[-1], "type"),
                    "id": get(resp[-1], "id"),
                }

        return cards

    def get_card(self, node_id: str, shelf_nr: int, card_nr: int):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {"object": {"type": "Card", "id": {"shelf": shelf_nr, "card": card_nr}}},
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    # <------------------------------------------------------------------------------------------------------------ PON

    def list_card_pons(self, node_id: str, shelf_nr: int, card_nr: int):
        more = True
        pons = []
        after_filter = {}

        while more:
            # Assemble payload
            action_args = {
                "object": {
                    "type": "Card",
                    "id": {
                        "shelf": shelf_nr,
                        "card": card_nr,
                    },
                    "children": {"type": "GponPort"},
                }
            }
            if after_filter:
                action_args["object"]["children"]["after"] = after_filter

            payload = self.generate_payload(
                node_id,
                "get-config",
                action_args,
            )

            # Send payload and process response
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            pons.extend(resp)

            # Assemble after filter
            if more and len(resp) > 0:
                after_filter = {
                    "type": get(resp[-1], "type"),
                    "id": get(resp[-1], "id"),
                }

        return pons

    def get_pon(self, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {
                "object": {
                    "type": "GponPort",
                    "id": {"shelf": shelf_nr, "card": card_nr, "gponport": pon_nr},
                }
            },
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    # <------------------------------------------------------------------------------------------------------------ ONT

    def list_pon_onts(self, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int):
        """
        todo list pon onts docs
        :param node_id:
        :param shelf_nr:
        :param card_nr:
        :param pon_nr:
        :return:
        """
        onts = []
        more = True
        after_filter = {}

        while more:
            # Build parameters
            params = {
                "action-type": "show-ont-brief",
                "action-args": {
                    "linked-pon": {
                        "type": "GponPort",
                        "id": {
                            "shelf": shelf_nr,
                            "card": card_nr,
                            "gponport": pon_nr,
                        },
                    },
                    # "subscr-id": "enelson",  # todo this is a filter
                },
            }
            if after_filter:
                params["action-args"]["after"] = after_filter

            # Generate and send payload
            payload = self.generate_payload(
                node_id,
                "action",
                params,
            )
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config",
            )
            onts.extend(resp)

            # Assemble after filter
            if more and len(onts) > 0:
                after_filter = get(onts[-1], "object")

        return onts

    def list_node_onts(self, node_id: str):
        more = True
        onts = []
        after_filter = {}

        while more:
            # Assemble payload
            action_args = {
                "object": {
                    "type": "System",
                    "id": None,
                    "children": {"type": "Ont"},
                }
            }
            if after_filter:
                action_args["object"]["children"]["after"] = after_filter

            payload = self.generate_payload(
                node_id,
                "get-config",
                action_args,
            )

            # Send payload and process response
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            onts.extend(resp)

            # Assemble after filter
            if more and len(resp) > 0:
                after_filter = {
                    "type": get(resp[-1], "type"),
                    "id": get(resp[-1], "id"),
                }

        return onts

    def get_ont_location(
        self, node_id: str, ont_id: int, _operation_type: str = "get-config"
    ):
        """

        :param node_id:
        :param ont_id:
        :param _operation_type:
        :return:
        """
        payload = self.generate_payload(
            node_id,
            _operation_type,
            {
                "object": {
                    "type": "Ont",
                    "id": {"ont": ont_id},
                }
            },
        )
        resp, more = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    def get_ont_status(self, node_id: str, ont_id: int):
        return self.get_ont_location(node_id, ont_id, _operation_type="get")

    def get_ont_errors(
        self, node_id: str, ont_id: int, interval: str = "1-day", count: int = 8
    ):
        return self.get_table(
            node_id,
            "show-ont-pm",
            {"type": "Ont", "id": {"ont": ont_id}},
            interval,
            count,
        )

    def clear_ont_errors(
        self, node_id: str, ont_id: int, interval: str = "1-day", count: int = 1
    ):
        return self.clear_table(
            node_id,
            "clear-ont-pm",
            {
                "type": "Ont",
                "id": {"ont": ont_id},
            },
            interval,
            count,
        )

    # <------------------------------------------------------------------------------------------------------ ONT Ports

    def list_ont_ports(
        self,
        node_id: str,
        ont_id: int,
        port_types: Iterable[str] = (
            "OntRg",
            "OntFb",
            "OntEthGe",
            "OntEthFe",
            "OntEthHpna",
            "OntPots",
            "OntDs1",
            "OntRfAvo",
            "OntVideoRf",
            "OntVideoHotRf",
        ),
    ):
        ports = []
        for port_type in port_types:
            more = True
            params = {
                "object": {
                    "type": "Ont",
                    "id": {
                        "ont": ont_id,
                    },
                    "children": {"type": port_type},
                }
            }
            while more:
                payload = self.generate_payload(node_id, "get-config", params)
                resp, more = self.post(
                    payload,
                    unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
                )

                if more and len(resp):
                    params["object"]["children"]["after"] = {"id": get(resp, "id")}

                if resp != [None]:
                    ports.extend(resp)

        return ports

    def get_ont_port_location(
        self,
        node_id: str,
        ont_id: int,
        port_type: str,
        port_nr: int,
        _operation_type: str = "get-config",
    ):
        params = {
            "object": {
                "type": port_type,
                "id": {
                    "ont": ont_id,
                    "ontslot": get(self.ont_slot_table, port_type),
                    port_type.lower(): port_nr,
                },
            }
        }
        if params["object"]["id"]["ontslot"] is None:
            params["object"]["id"].pop("ontslot")
        payload = self.generate_payload(node_id, _operation_type, params)

        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp

    def get_ont_port_status(
        self, node_id: str, ont_id: int, port_type: str, port_nr: int
    ):
        return self.get_ont_port_location(
            node_id, ont_id, port_type, port_nr, _operation_type="get"
        )

    def get_ont_port_leases(
        self, node_id: str, ont_id: int, port_type: str, port_nr: int
    ):
        ont_location = {
            "type": port_type,
            "id": {
                "ont": ont_id,
                "ontslot": get(self.ont_slot_table, port_type),
                port_type.lower(): port_nr,
            },
        }
        if ont_location["id"]["ontslot"] is None:
            ont_location["id"].pop("ontslot")
        return self.get_leases(node_id, ont_location)

    # <----------------------------------------------------------------------------------------------------------- XDSL

    def list_card_xdsl(self, node_id: str, shelf_nr: int, card_nr: int):
        params = {
            "object": {
                "type": "Card",
                "id": {
                    "shelf": shelf_nr,
                    "card": card_nr,
                },
                "children": {"type": "DslPort"},
            }
        }
        more = True
        modems = []

        while more:
            payload = self.generate_payload(
                node_id,
                "get-config",
                params,
            )
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            modems.extend(resp)

            if more and len(resp) > 0:
                params["object"]["children"]["after"] = {
                    "type": resp[-1]["type"],
                    "id": resp[-1]["id"],
                }

        return modems

    def get_xdsl_port_provisioning(
        self, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
    ):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {
                "object": {
                    "type": "DslPort",
                    "id": {
                        "shelf": shelf_nr,
                        "card": card_nr,
                        "dslport": port_nr,
                    },
                }
            },
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp[0]

    def get_xdsl_port_status(
        self, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
    ):
        payload = self.generate_payload(
            node_id,
            "get",
            {
                "object": {
                    "type": "DslPort",
                    "id": {
                        "shelf": shelf_nr,
                        "card": card_nr,
                        "dslport": port_nr,
                    },
                }
            },
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp[0]

    def get_xdsl_port_eth_performance(
        self,
        node_id: str,
        shelf_nr: int,
        card_nr: int,
        port_nr: int,
        interval: str = "1-day",
        count: int = 1,
    ):
        return self.get_table(
            node_id,
            "show-eth-pm",
            {
                "type": "DslPort",
                "id": {"shelf": shelf_nr, "card": card_nr, "dslport": port_nr},
            },
            interval,
            count,
        )

    def clear_xdsl_port_eth_performance(
        self,
        node_id: str,
        shelf_nr: int,
        card_nr: int,
        port_nr: int,
        interval: str = "1-day",
        count: int = 1,
    ):
        return self.clear_table(
            node_id,
            "clear-eth-pm",
            {
                "type": "DslPort",
                "id": {"shelf": shelf_nr, "card": card_nr, "dslport": port_nr},
            },
            interval,
            count,
        )

    def get_xdsl_port_dsl_performance(
        self,
        node_id: str,
        shelf_nr: int,
        card_nr: int,
        port_nr: int,
        interval: str = "1-day",
        count: int = 1,
    ):
        return self.get_table(
            node_id,
            "show-dsl-pm",
            {
                "type": "DslPort",
                "id": {"shelf": shelf_nr, "card": card_nr, "dslport": port_nr},
            },
            interval,
            count,
        )

    def clear_xdsl_port_dsl_performance(
        self,
        node_id: str,
        shelf_nr: int,
        card_nr: int,
        port_nr: int,
        interval: str = "1-day",
        count: int = 1,
    ):
        return self.clear_table(
            node_id,
            "clear-dsl-pm",
            {
                "type": "DslPort",
                "id": {"shelf": shelf_nr, "card": card_nr, "dslport": port_nr},
            },
            interval,
            count,
        )

    def get_xdsl_ai_provisioning(
        self, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
    ):
        payload = self.generate_payload(
            node_id,
            "get-config",
            {
                "object": {
                    "type": "EthIntf",
                    "id": {
                        "shelf": shelf_nr,
                        "card": card_nr,
                        "ethintf": port_nr,  # 200 + port
                    },
                }
            },
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object",
        )
        return resp[0]

    def get_xdsl_leases(self, node_id: str, shelf_nr: int, card_nr: int, port_nr: int):
        port_location = {
            "type": "EthIntf",
            "id": {
                "shelf": shelf_nr,
                "card": card_nr,
                "ethintf": port_nr,
            },
        }
        return self.get_leases(node_id, port_location)

    # <----------------------------------------------------------------------------------------------------------- POTS

    def list_card_pots(self, node_id: str, shelf_nr: int, pots_nr: int):
        params = {
            "object": {
                "type": "Card",
                "id": {
                    "shelf": shelf_nr,
                    "card": pots_nr,  # 200 + port
                },
                "children": {"type": "Pots"},
            }
        }
        more = True
        pots_entries = []

        while more:
            payload = self.generate_payload(
                node_id,
                "get-config",
                params,
            )
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
            )
            pots_entries.extend(resp)

            if more and len(resp) > 0:
                params["object"]["children"]["after"] = {
                    "type": resp[-1]["type"],
                    "id": resp[-1]["id"],
                }

        return pots_entries

    # <-------------------------------------------------------------------------------------------------------- Utility

    def get_table(
        self,
        node_id: str,
        action_type: str,
        object_info: dict,
        interval: str,
        count: int,
    ):
        entries = []
        more = True
        params = {
            "action-type": action_type,
            "action-args": {
                "object": object_info,
                "bin-type": interval,
                "start-bin": 1,
                "count": count,
            },
        }

        while more:
            # Generate and send payload
            payload = self.generate_payload(
                node_id,
                "action",
                params,
            )
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.bin",
            )
            entries.extend(resp)

            # Assemble after filter
            if more and len(entries) > 0:
                params["action-args"]["start-bin"] = len(entries) + 1
                params["action-args"]["count"] = count - len(entries)

        return entries

    def clear_table(
        self,
        node_id: str,
        action_type: str,
        object_info: dict,
        interval: str,
        count: int,
    ):
        params = {
            "action-type": action_type,
            "action-args": {
                "object": object_info,
                "bin-type": interval,
                "start-bin": 1,
                "count": count,
            },
        }

        # Generate and send payload
        payload = self.generate_payload(
            node_id,
            "action",
            params,
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply",
        )
        if isinstance(resp[0], dict) and "ok" in resp[0]:
            return True
        return False

    def get_leases(self, node_id: str, port_info: dict):
        params = {
            "action-type": "show-dhcp-leases",
            "action-args": {
                "object": port_info,
            },
        }
        print(params)

        leases = []
        more = True
        while more:
            # Generate and send payload
            payload = self.generate_payload(
                node_id,
                "action",
                params,
            )
            resp, more = self.post(
                payload,
                unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply.action-reply",
            )
            leases.extend(resp)

            # Assemble after filter
            if more and len(leases) > 0:
                params["action-args"]["after"] = {
                    "mac": get(leases[-1], "entry.mac")
                }  # todo untested, idk if this will work

        return leases

    def delete_lease(self, node_id: str, ip_address: str, mac_address: str):
        params = {
            "action-type": "delete-dhcp-lease",
            "action-args": {
                "ip": ip_address,
                "mac": mac_address,
            },
        }

        payload = self.generate_payload(
            node_id,
            "action",
            params,
        )
        resp, _ = self.post(
            payload,
            unpack_level="soapenv:Envelope.soapenv:Body.rpc-reply",
        )
        if isinstance(resp[0], dict) and "ok" in resp[0]:
            return True
        return False

    @property
    def message_id(self):
        return str(random.getrandbits(random.randint(2, 31)))

    def generate_payload(
        self, node_id: str, action: str, params: Mapping[str, Any]
    ) -> str:
        """
        Generates a payload ready to be sent to the CMS server.
        :param node_id: ex: lab
        :param action: ex: action
        :param params: ex: {"action-type": "show-dhcp-leases", "action-args": {"object": {"type": "OntEthGe", "id": {"ont": 1, "ontslot": 3, "ontethge": 1}}}}
        :return:
        :raises: xmltodict.ParsingInterrupted if params has an invalid format
        """
        # Generate envelope
        soapenv = "www.w3.org/2003/05/soap-envelope"
        if action == "auth":
            soapenv = "http://schemas.xmlsoap.org/soap/envelope/"

        payload = {
            "soapenv:Envelope": {
                "@xmlns:soapenv": soapenv,
            }
        }

        # Build payload for auth request
        if action == "auth":
            payload["soapenv:Envelope"]["soapenv:Body"] = {
                "auth": {
                    "@message-id": self.message_id,
                }
            }
            payload["soapenv:Envelope"]["soapenv:Body"]["auth"].update(params)

        elif action == "action":
            payload["soapenv:Envelope"]["soapenv:Body"] = {
                "rpc": {
                    "@message-id": self.message_id,
                    "@nodename": "NTWK-" + node_id,
                    "@username": self.username,
                    "@sessionid": self.session_id,
                }
            }
            payload["soapenv:Envelope"]["soapenv:Body"]["rpc"][action] = params

        elif action in ["get", "get-config"]:
            payload["soapenv:Envelope"]["soapenv:Body"] = {
                "rpc": {
                    "@message-id": self.message_id,
                    "@nodename": "NTWK-" + node_id,
                    "@username": self.username,
                    "@sessionid": self.session_id,
                }
            }

            payload["soapenv:Envelope"]["soapenv:Body"]["rpc"][action] = {
                "source": {"running": None},
                "filter": {"@type": "subtree", "top": params},
            }

            if action == "get":
                payload["soapenv:Envelope"]["soapenv:Body"]["rpc"][action].pop("source")

        return xmltodict.unparse(payload)

    def post(
        self, payload: str, unpack_level: str = "", timeout: int = 10
    ) -> (List[dict], bool):
        """
        Sends a PORT request to the cms server with the payload and returns the response as a JSON object.
        :param payload: A request ready to be sent to the CMS server
        :param unpack_level: A list of keys to automatically tree into the response to remove excess, represented as items separated by periods, ex: soapenv:Envelope.soapenv:Body
        :param timeout: Request timeout in seconds
        :return: resp, more
        """
        try:
            resp = requests.post(
                url=f"http://{self.ip}:18080/cmsexc/ex/netconf",
                headers={
                    "Content-Type": "text/xml;charset=ISO8859-1",
                    "User-Agent": f"CMS_NBI_CONNECT-{self.username}",
                },
                data=payload,
                timeout=timeout,
            )

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Post request to CMS server at {self.ip} failed")
            self.logger.error(e)
            raise CmsCommunicationFailure(self.ip)

        try:
            data = xmltodict.parse(resp.content)
            # Check for errors
            print(json.dumps(data, indent=2))
            # todo

            # Check for auth errors
            if (
                get(resp, "Envelope.Body.auth-reply")
                and get(resp, "Envelope.Body.auth-reply.ResultCode") != "0"
            ):
                raise CmsAuthenticationFailure(self.username, self.ip)

            # Check for rpc errors
            if get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply") and "ok" not in get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply"
            ):
                raise CmsCommunicationFailure(self.ip)

            # Unpack
            if unpack_level:
                data = get(data, unpack_level, default=[])
            if not isinstance(data, list):
                data = [data]

            return data, "<more/>" in str(resp.content)

        except xmltodict.ParsingInterrupted as e:
            self.logger.error(f"CMS server at {self.ip} returned invalid XML")
            self.logger.error(resp.content)
            self.logger.error(e)
            raise CmsCommunicationFailure(self.ip)

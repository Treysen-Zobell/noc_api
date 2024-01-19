# Standard Library Imports
import json
from typing import Any

import requests
# Third Party Imports
from fastapi import APIRouter, Request

from app.models.modem import ModemStatus, ModemPerformance, Modem, ModemAction, XDSLLineTest, NodeAlarms
# Local App Imports
from app.models.ont import OntGeneral, OntStatus, OntPerformance, OntPort, OntService, OntAction, OntVoice

router = APIRouter(prefix="/v1/cms", tags=["cms"])


@router.get("/ont/{node_id}/{ont_id}",
            summary="Gets programmed ONT (Optical Network Terminal) information.",
            description="""Retrieves programmed ONT information, including the ONT's admin state, serial number, and description, given the ONT's node and ID. The ID corresponds to the number next to the ONT entry in the CMS side panel.""")
def get_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntGeneral:
    cms = request.app.state.cms
    return cms.get_ont(node_id, ont_id)


@router.get("/ont/{node_id}/{ont_id}/status",
            summary="Gets real-time ONT information.",
            description="Retrieves real-time information about an ONT, including its operational state, alarms, and light levels.")
def get_ont_status(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntStatus:
    cms = request.app.state.cms
    return cms.get_ont_status(node_id, ont_id)


@router.get("/ont/{node_id}/{ont_id}/performance",
            summary="Gets the current BIP (Background Interference Pattern) errors on an ONT.",
            description="Retrieves the current BIP errors on a specific ONT.")
def get_ont_performance(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntPerformance:
    cms = request.app.state.cms
    return OntPerformance(**cms.get_ont_performance(node_id, ont_id))


@router.get("/ont/{node_id}/{ont_id}/port/{port_number}",
            summary="Gets the current GE port information for an ONT.")
def get_ont_port_info(
        request: Request,
        node_id: str,
        ont_id: str,
        port_number: int
) -> OntPort:
    cms = request.app.state.cms
    return cms.get_ont_port(node_id, ont_id, port_number)


@router.get("/ont/{node_id}/{ont_id}/port/{port_number}/service",
            summary="Gets the service information for a GE port on an ONT.")
def get_ont_port_service(
        request: Request,
        node_id: str,
        ont_id: str,
        port_number: int
) -> OntService:
    cms = request.app.state.cms
    return cms.get_ont_port_data_service(node_id, ont_id, port_number)


@router.get("/ont/{node_id}/{ont_id}/port/{port_number}/voice",
            summary="Gets the voice service information for a port on an ONT.")
def get_ont_voice_port(
        request: Request,
        node_id: str,
        ont_id: str,
        port_number: int
) -> OntVoice:
    cms = request.app.state.cms
    return cms.get_ont_voice_service(node_id, ont_id, port_number)


@router.get("/ont/{node_id}/{ont_id}/performance/reset",
            summary="Gets the current BIP (Background Interference Pattern) errors on an ONT.",
            description="Retrieves the current BIP errors on a specific ONT.")
def reset_ont_performance(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntPerformance:
    cms = request.app.state.cms
    return cms.reset_ont_performance(node_id, ont_id)


@router.get("/ont/{node_id}/{ont_id}/reset",
            summary="Resets an ONT.",
            description="Initiates a reset operation on a specific ONT.")
def reset_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.reset_ont(node_id, ont_id), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/quarantine",
            summary="Enters an ONT into quarantine.",
            description="Puts a specific ONT into quarantine.")
def quarantine_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.quarantine_ont(node_id, ont_id), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/release",
            summary="Removes an ONT from quarantine.",
            description="Releases a specific ONT from quarantine.")
def release_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.release_ont(node_id, ont_id), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/disable",
            summary="Disables an ONT.",
            description="Sets the admin state of a specific ONT to disabled.")
def disable_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.disable_ont(node_id, ont_id), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/{port_nr}/disable",
            summary="Disables an ONT port.",
            description="Sets the admin state of a specific ONT port to disabled.")
def disable_ont_port(
        request: Request,
        node_id: str,
        ont_id: str,
        port_nr: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.disable_ont_port(node_id, ont_id, port_nr), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/enable",
            summary="Enables an ONT.",
            description="Sets the admin state of a specific ONT to enabled.")
def enable_ont(
        request: Request,
        node_id: str,
        ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.enable_ont(node_id, ont_id), additional_info="")


@router.get("/ont/{node_id}/{ont_id}/{port_nr}/enable",
            summary="Enables an ONT port.",
            description="Sets the admin state of a specific ONT port to enabled.")
def enable_ont_port(
        request: Request,
        node_id: str,
        ont_id: str,
        port_nr: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.enable_ont_port(node_id, ont_id, port_nr), additional_info="")


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}",
            summary="Gets programmed information for a modem.",
            description="Retrieves information such as the admin state and template for an xDSL modem.")
def get_xdsl(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        interface_id: str,
) -> Modem:
    cms = request.app.state.cms
    return Modem(port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                 associated_interface=cms.get_xdsl_interface(node_id, shelf_nr, card_nr, interface_id))


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/status",
            summary="Gets real-time information about a modem.",
            description="Retrieves information such as SNR (Signal-to-Noise Ratio) levels, attainable rates, and current rates for an xDSL modem.")
def get_xdsl_status(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        interface_id: str,
) -> ModemStatus:
    cms = request.app.state.cms
    return cms.get_xdsl_status(node_id, shelf_nr, card_nr, interface_id)


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/performance",
            summary="Gets a modem's code violations.",
            description="Retrieves code violations for an xDSL modem.")
def get_xdsl_performance(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        interface_id: str,
) -> ModemPerformance:
    cms = request.app.state.cms
    return cms.get_xdsl_performance(node_id, shelf_nr, card_nr, interface_id)


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/enable",
            summary="Enables a modem's connection.",
            description="Sets an xDSL modem's admin state to enabled.")
def enable_xdsl_port(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        interface_id: str,
) -> ModemAction:
    cms = request.app.state.cms
    return ModemAction(success=cms.enable_xdsl_port(node_id, shelf_nr, card_nr, interface_id), additional_info="")


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/disable",
            summary="Disables a modem's connection.",
            description="Sets an xDSL modem's admin state to disabled.")
def disable_xdsl_port(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        interface_id: str,
) -> ModemAction:
    cms = request.app.state.cms
    return ModemAction(success=cms.disable_xdsl_port(node_id, shelf_nr, card_nr, interface_id), additional_info="")


@router.get("/xdsl/{node_id}/{shelf_nr}/{card_nr}/{pots_id}/line_test",
            summary="Runs a line test on a DSL (Digital Subscriber Line) phone line.",
            description="Initiates a line test on a DSL phone line, typically used for testing POTS (Plain Old Telephone Service) connections.")
def run_xdsl_line_test(
        request: Request,
        node_id: str,
        shelf_nr: str,
        card_nr: str,
        pots_id: str,
) -> XDSLLineTest:
    cms = request.app.state.cms
    return cms.run_xdsl_line_test(node_id, shelf_nr, card_nr, pots_id)


@router.get("/node/{node_id}/alarms",
            summary="Gets all current alarms on a node")
def get_node_alarms(
        request: Request,
        node_id: str,
) -> NodeAlarms:
    cms = request.app.state.cms
    return cms.get_node_alarms(node_id)


@router.get("/budibase/{bid}/enable",
            summary="Enables a broadband service based on the BID (Broadband Identifier).",
            description="Enables a broadband service based on the BID. This route is designed to handle enabling ONTs and xDSL connections.")
def smart_enable_bid(
        request: Request,
        bid: str,
) -> ModemAction | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}")
        resp = json.loads(resp.content)
        resp = [r for r in resp if r["bid"] == bid]
        resp = resp[0]

        node_id, full_id = resp["port_full"].split(" ")

        if resp["tech"] == "FIBER":
            if "g" in full_id.split("-")[-1]:
                ont_id, port_nr = full_id.split("-")[-2:]
                return OntAction(success=cms.enable_ont_port(node_id, ont_id, port_nr.replace("g", "")),
                                 additional_info=f"Enabled fiber port {port_nr}.")
            else:
                ont_id = full_id.split("-")[-1]
                return OntAction(success=cms.enable_ont_port(node_id, ont_id, "1"),
                                 additional_info="Enabled fiber port g1.")

        elif resp["tech"] == "COPPER":
            shelf_nr, card_nr, interface_id = full_id.split("-")
            data = cms.get_xdsl(
                node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return ModemAction(success=cms.enable_xdsl_bonding_group(node_id, shelf_nr, card_nr, interface_id),
                                   additional_info="Enabled bonded XDSL group.")

            else:
                return ModemAction(success=cms.enable_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                                   additional_info="Enabled XDSL port.")

        else:
            return OntAction(success=False, additional_info=f"Unable to disable bid with tech {resp['tech']}")

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))


@router.get("/budibase/{bid}/disable",
            summary="Disables a broadband service based on the BID (Broadband Identifier).",
            description="Disables a broadband service based on the BID. This route is designed to handle disabling ONTs and xDSL connections.")
def smart_disable_bid(
        request: Request,
        bid: str,
) -> ModemAction | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}")
        resp = json.loads(resp.content)
        resp = [r for r in resp if r["bid"] == bid]
        resp = resp[0]

        node_id, full_id = resp["port_full"].split(" ")

        if resp["tech"] == "FIBER":
            if "g" in full_id.split("-")[-1]:
                ont_id, port_nr = full_id.split("-")[-2:]
                return OntAction(success=cms.disable_ont_port(node_id, ont_id, port_nr.replace("g", "")),
                                 additional_info=f"Disabled fiber port {port_nr}")
            else:
                ont_id = full_id.split("-")[-1]
                return OntAction(success=cms.disable_ont_port(node_id, ont_id, "1"),
                                 additional_info="Disabled fiber port g1.")

        elif resp["tech"] == "COPPER":
            shelf_nr, card_nr, interface_id = full_id.split("-")
            data = cms.get_xdsl(
                node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return ModemAction(success=cms.disable_xdsl_bonding_group(node_id, shelf_nr, card_nr, interface_id),
                                   additional_info="Disabled XDSL bonding group.")

            else:
                return ModemAction(success=cms.disable_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                                   additional_info="Disabled XDSL port.")

        else:
            return OntAction(success=False, additional_info=f"Unable to disable bid with tech {resp['tech']}")

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))


@router.get("/budibase/rogue/{node_id}/{shelf_nr}/{card_nr}/{gpon_nr}",
            summary="Detect rogue ONTs.",
            description="This call checks all ont's on a gpon. It gets their performance info, such as their gemhec errors. It sorts the final result by the sum of the bip up and down in reverse order.")
def detect_rogues(
        request: Request,
        node_id: str,
        shelf_nr: int,
        card_nr: int,
        gpon_nr: int,
) -> dict[str, int | list[Any]]:
    cms = request.app.state.cms
    onts = cms.list_onts_on_gpon(node_id, shelf_nr, card_nr, gpon_nr)

    results = {"onts": [], "count": 0}
    for ont_id in onts:
        ont_performance = cms.get_ont_performance(node_id, ont_id)
        if ont_performance["bip_errors_up"] is not None and ont_performance["bip_errors_down"] is not None:
            results["onts"].append(ont_performance)
            results["count"] += 1
    return results


@router.get("/budibase/{bid}/general",
            summary="Gets broadband service programmed information from the BID (Broadband Identifier).",
            description="Gets programmed device info based on the BID. This route is designed to handle disabling ONTs and xDSL connections.")
def smart_get_general(
        request: Request,
        bid: str,
) -> Modem | OntGeneral | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}")
        resp = json.loads(resp.content)
        resp = [r for r in resp if r["bid"] == bid]
        resp = resp[0]

        node_id, full_id = resp["port_full"].split(" ")

        if resp["tech"] == "FIBER":
            if "g" in full_id.split("-")[-1]:
                ont_id, _ = full_id.split("-")[-2:]
                return OntGeneral(**cms.get_ont(node_id, ont_id))
            else:
                ont_id = full_id.split("-")[-1]
                return OntGeneral(**cms.get_ont(node_id, ont_id))

        elif resp["tech"] == "COPPER":
            shelf_nr, card_nr, interface_id = full_id.split("-")
            data = cms.get_xdsl(
                node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return Modem(port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                             associated_interface=cms.get_xdsl_interface(node_id, shelf_nr, card_nr, interface_id))

            else:
                return Modem(port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                             associated_interface=cms.get_xdsl_interface(node_id, shelf_nr, card_nr, interface_id))

        else:
            return OntAction(success=False, additional_info=f"Unable to disable bid with tech {resp['tech']}")

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))

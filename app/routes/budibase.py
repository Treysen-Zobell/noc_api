# Standard Library Imports
import json
from typing import Any

import requests

# Third Party Imports
from fastapi import APIRouter, Request

from app.models.modem import (
    Modem,
    ModemAction,
)

# Local App Imports
from app.models.ont import (
    OntGeneral,
    OntAction,
)


router = APIRouter(prefix="/v1/budibase", tags=["budibase", "cms"])


@router.patch(
    "/bid/{bid}/enable",
    summary="Enables a broadband service based on the BID (Broadband Identifier).",
    description="Enables a broadband service based on the BID. This route is designed to handle enabling ONTs and xDSL connections.",
)
def smart_enable_bid(
    request: Request,
    bid: str,
) -> ModemAction | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}"
        )
        resp = json.loads(resp.content)
        resp = [r for r in resp if r["bid"] == bid]
        resp = resp[0]

        node_id, full_id = resp["port_full"].split(" ")

        if resp["tech"] == "FIBER":
            if "g" in full_id.split("-")[-1]:
                ont_id, port_nr = full_id.split("-")[-2:]
                return OntAction(
                    success=cms.enable_ont_port(
                        node_id, ont_id, port_nr.replace("g", "")
                    ),
                    additional_info=f"Enabled fiber port {port_nr}.",
                )
            else:
                ont_id = full_id.split("-")[-1]
                return OntAction(
                    success=cms.enable_ont_port(node_id, ont_id, "1"),
                    additional_info="Enabled fiber port g1.",
                )

        elif resp["tech"] == "COPPER":
            shelf_nr, card_nr, interface_id = full_id.split("-")
            data = cms.get_xdsl(node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return ModemAction(
                    success=cms.enable_xdsl_bonding_group(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                    additional_info="Enabled bonded XDSL group.",
                )

            else:
                return ModemAction(
                    success=cms.enable_xdsl_port(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                    additional_info="Enabled XDSL port.",
                )

        else:
            return OntAction(
                success=False,
                additional_info=f"Unable to disable bid with tech {resp['tech']}",
            )

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))


@router.patch(
    "/bid/{bid}/disable",
    summary="Disables a broadband service based on the BID (Broadband Identifier).",
    description="Disables a broadband service based on the BID. This route is designed to handle disabling ONTs and xDSL connections.",
)
def smart_disable_bid(
    request: Request,
    bid: str,
) -> ModemAction | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}"
        )
        resp = json.loads(resp.content)
        resp = [r for r in resp if r["bid"] == bid]
        resp = resp[0]

        node_id, full_id = resp["port_full"].split(" ")

        if resp["tech"] == "FIBER":
            if "g" in full_id.split("-")[-1]:
                ont_id, port_nr = full_id.split("-")[-2:]
                return OntAction(
                    success=cms.disable_ont_port(
                        node_id, ont_id, port_nr.replace("g", "")
                    ),
                    additional_info=f"Disabled fiber port {port_nr}",
                )
            else:
                ont_id = full_id.split("-")[-1]
                return OntAction(
                    success=cms.disable_ont_port(node_id, ont_id, "1"),
                    additional_info="Disabled fiber port g1.",
                )

        elif resp["tech"] == "COPPER":
            shelf_nr, card_nr, interface_id = full_id.split("-")
            data = cms.get_xdsl(node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return ModemAction(
                    success=cms.disable_xdsl_bonding_group(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                    additional_info="Disabled XDSL bonding group.",
                )

            else:
                return ModemAction(
                    success=cms.disable_xdsl_port(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                    additional_info="Disabled XDSL port.",
                )

        else:
            return OntAction(
                success=False,
                additional_info=f"Unable to disable bid with tech {resp['tech']}",
            )

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))


@router.get(
    "/gpon/{node_id}/{shelf_nr}/{card_nr}/{gpon_nr}/rogue",
    summary="Detect rogue ONTs.",
    description="This call checks all ont's on a gpon. It gets their performance info, such as their gemhec errors. It sorts the final result by the sum of the bip up and down in reverse order.",
)
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
        if (
            ont_performance["bip_errors_up"] is not None
            and ont_performance["bip_errors_down"] is not None
        ):
            results["onts"].append(ont_performance)
            results["count"] += 1
    return results


@router.get(
    "/bid/{bid}/general",
    summary="Gets broadband service programmed information from the BID (Broadband Identifier).",
    description="Gets programmed device info based on the BID. This route is designed to handle disabling ONTs and xDSL connections.",
)
def smart_get_general(
    request: Request,
    bid: str,
) -> Modem | OntGeneral | OntAction:
    try:
        cms = request.app.state.cms

        resp = requests.get(
            f"http://10.225.254.80/subscriber/broadband/search/all/{bid}"
        )
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
            data = cms.get_xdsl(node_id, shelf_nr, card_nr, interface_id)

            if data["bonded_interface_id"] is not None:
                interface_id = data["bonded_interface_id"]
                return Modem(
                    port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                    associated_interface=cms.get_xdsl_interface(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                )

            else:
                return Modem(
                    port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
                    associated_interface=cms.get_xdsl_interface(
                        node_id, shelf_nr, card_nr, interface_id
                    ),
                )

        else:
            return OntAction(
                success=False,
                additional_info=f"Unable to disable bid with tech {resp['tech']}",
            )

    except Exception as e:
        return OntAction(success=False, additional_info=str(e))

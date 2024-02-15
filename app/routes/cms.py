# Standard Library Imports
import json
from typing import Any

import requests

# Third Party Imports
from fastapi import APIRouter, Request

from app.models.modem import (
    ModemStatus,
    ModemPerformance,
    Modem,
    ModemAction,
    XDSLLineTest,
    NodeAlarms,
)

# Local App Imports
from app.models.ont import (
    OntGeneral,
    OntStatus,
    OntPerformance,
    OntPort,
    OntService,
    OntAction,
    OntVoice,
)

router = APIRouter(prefix="/v1/cms", tags=["cms"])


@router.get(
    "/ont/{node_id}/{ont_id}",
    summary="Gets programmed ONT information.",
)
def get_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntGeneral:
    cms = request.app.state.cms
    return cms.get_ont(node_id, ont_id)


@router.get(
    "/ont/{node_id}/{ont_id}/status",
    summary="Gets real-time ONT information.",
)
def get_ont_status(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntStatus:
    cms = request.app.state.cms
    return cms.get_ont_status(node_id, ont_id)


@router.get(
    "/ont/{node_id}/{ont_id}/performance",
    summary="Gets the current BIP errors on an ONT.",
)
def get_ont_performance(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntPerformance:
    cms = request.app.state.cms
    return OntPerformance(**cms.get_ont_performance(node_id, ont_id))


@router.get(
    "/ont/{node_id}/{ont_id}/port/{port_number}",
    summary="Gets the current GE port information for an ONT.",
)
def get_ont_port_info(
    request: Request, node_id: str, ont_id: str, port_number: int
) -> OntPort:
    cms = request.app.state.cms
    return cms.get_ont_port(node_id, ont_id, port_number)


@router.get(
    "/ont/{node_id}/{ont_id}/port/{port_number}/service",
    summary="Gets the service information for a GE port on an ONT.",
)
def get_ont_port_service(
    request: Request, node_id: str, ont_id: str, port_number: int
) -> OntService:
    cms = request.app.state.cms
    return cms.get_ont_port_data_service(node_id, ont_id, port_number)


@router.get(
    "/ont/{node_id}/{ont_id}/port/{port_number}/voice",
    summary="Gets the voice service information for a port on an ONT.",
)
def get_ont_voice_port(
    request: Request, node_id: str, ont_id: str, port_number: int
) -> OntVoice:
    cms = request.app.state.cms
    return cms.get_ont_voice_service(node_id, ont_id, port_number)


@router.patch(
    "/ont/{node_id}/{ont_id}/performance/reset",
    summary="Resets the BIP errors for the past week to 0.",
)
def reset_ont_performance(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntPerformance:
    cms = request.app.state.cms
    return cms.reset_ont_performance(node_id, ont_id)


@router.patch(
    "/ont/{node_id}/{ont_id}/reset",
    summary="Resets an ONT.",
)
def reset_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.reset_ont(node_id, ont_id), additional_info="")


@router.patch(
    "/ont/{node_id}/{ont_id}/quarantine",
    summary="Puts an ONT into quarantine.",
)
def quarantine_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.quarantine_ont(node_id, ont_id), additional_info="")


@router.patch(
    "/ont/{node_id}/{ont_id}/release",
    summary="Removes an ONT from quarantine.",
)
def release_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.release_ont(node_id, ont_id), additional_info="")


@router.patch(
    "/ont/{node_id}/{ont_id}/disable",
    summary="Disables an ONT.",
    description="Sets the admin state of a specific ONT to disabled.",
)
def disable_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.disable_ont(node_id, ont_id), additional_info="")


@router.patch(
    "/ont/{node_id}/{ont_id}/{port_nr}/disable",
    summary="Disables an ONT port.",
    description="Sets the admin state of a specific ONT port to disabled.",
)
def disable_ont_port(
    request: Request,
    node_id: str,
    ont_id: str,
    port_nr: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(
        success=cms.disable_ont_port(node_id, ont_id, port_nr), additional_info=""
    )


@router.patch(
    "/ont/{node_id}/{ont_id}/enable",
    summary="Enables an ONT.",
    description="Sets the admin state of a specific ONT to enabled.",
)
def enable_ont(
    request: Request,
    node_id: str,
    ont_id: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(success=cms.enable_ont(node_id, ont_id), additional_info="")


@router.patch(
    "/ont/{node_id}/{ont_id}/{port_nr}/enable",
    summary="Enables an ONT port.",
    description="Sets the admin state of a specific ONT port to enabled.",
)
def enable_ont_port(
    request: Request,
    node_id: str,
    ont_id: str,
    port_nr: str,
) -> OntAction:
    cms = request.app.state.cms
    return OntAction(
        success=cms.enable_ont_port(node_id, ont_id, port_nr), additional_info=""
    )


@router.get(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}",
    summary="Gets programmed information for a modem.",
)
def get_xdsl(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    interface_id: str,
) -> Modem:
    cms = request.app.state.cms
    return Modem(
        port=cms.get_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
        associated_interface=cms.get_xdsl_interface(
            node_id, shelf_nr, card_nr, interface_id
        ),
    )


@router.get(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/status",
    summary="Gets real-time information about a modem.",
)
def get_xdsl_status(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    interface_id: str,
) -> ModemStatus:
    cms = request.app.state.cms
    return cms.get_xdsl_status(node_id, shelf_nr, card_nr, interface_id)


@router.get(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/performance",
    summary="Gets a modem's code violations.",
)
def get_xdsl_performance(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    interface_id: str,
) -> ModemPerformance:
    cms = request.app.state.cms
    return cms.get_xdsl_performance(node_id, shelf_nr, card_nr, interface_id)


@router.patch(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/enable",
    summary="Enables a modem's connection.",
    description="Sets an xDSL modem's admin state to enabled.",
)
def enable_xdsl_port(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    interface_id: str,
) -> ModemAction:
    cms = request.app.state.cms
    return ModemAction(
        success=cms.enable_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
        additional_info="",
    )


@router.patch(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{interface_id}/disable",
    summary="Disables a modem's connection.",
    description="Sets an xDSL modem's admin state to disabled.",
)
def disable_xdsl_port(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    interface_id: str,
) -> ModemAction:
    cms = request.app.state.cms
    return ModemAction(
        success=cms.disable_xdsl_port(node_id, shelf_nr, card_nr, interface_id),
        additional_info="",
    )


@router.get(
    "/xdsl/{node_id}/{shelf_nr}/{card_nr}/{pots_id}/line_test",
    summary="Runs a line test on a DSL phone line.",
    description="Initiates a line test on a DSL phone line, typically used for testing POTS connections.",
)
def run_xdsl_line_test(
    request: Request,
    node_id: str,
    shelf_nr: str,
    card_nr: str,
    pots_id: str,
) -> XDSLLineTest:
    cms = request.app.state.cms
    return cms.run_xdsl_line_test(node_id, shelf_nr, card_nr, pots_id)


@router.get("/node/{node_id}/alarms", summary="Gets all current alarms on a node")
def get_node_alarms(
    request: Request,
    node_id: str,
) -> NodeAlarms:
    cms = request.app.state.cms
    return cms.get_node_alarms(node_id)

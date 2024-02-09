from fastapi import APIRouter, Request, HTTPException
from app.services.cms import CmsClient

router = APIRouter(prefix="/v1/cms", tags=["cms"])


@router.get("/node", summary="List all nodes", description="Feature not implemented")
def list_nodes(request: Request):
    pass


@router.get(
    "/node/{node_id}",
    summary="Get node information",
    description="Exposed, needs data model",
)
def get_node(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.get_node(node_id)  # todo process reply


@router.get(
    "/node/{node_id}/alarm",
    summary="Get node alarms",
    description="Exposed, needs data model.",
)
def get_node_alarms(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.get_node_alarms(node_id)  # todo process reply


@router.get(
    "/node/{node_id}/shelf",
    summary="List all shelves on node",
    description="Exposed, needs data model.",
)
def list_shelves(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.list_node_shelves(node_id)


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}",
    summary="Get shelf information",
    description="Feature not implemented",
)
def get_shelf(request: Request, node_id: str, shelf_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_shelf(node_id, shelf_nr)  # todo process reply


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card",
    summary="List all cards on shelf",
    description="Exposed, needs data model.",
)
def list_cards(request: Request, node_id: str, shelf_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.list_shelf_cards(node_id, shelf_nr)


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}",
    summary="Get card information",
    description="Feature not implemented",
)
def get_card(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_card(node_id, shelf_nr, card_nr)  # todo process reply


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon",
    summary="List all pons on card",
    description="Exposed, needs data model.",
)
def list_pons(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.list_card_pons(node_id, shelf_nr, card_nr)


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon/{pon_nr}",
    summary="Get pon information",
    description="Feature not implemented",
)
def get_pon(request: Request, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_pon(node_id, shelf_nr, card_nr, pon_nr)  # todo process reply


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon/{pon_nr}/ont",
    summary="List all onts on pon",
    description="Exposed, needs data model",
)
def list_pon_onts(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.list_pon_onts(node_id, shelf_nr, card_nr, pon_nr)


@router.get(
    "/node/{node_id}/ont",
    summary="List all onts on node",
    description="Exposed, needs data model.",
)
def list_node_onts(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.list_node_onts(node_id)


@router.get(
    "/node/{node_id}/ont/{ont_id}/location",
    summary="Get ont location information",
    description="Exposed, needs data model",
)
def get_ont_location(request: Request, node_id: str, ont_id: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_location(node_id, ont_id)  # todo process reply


@router.get(
    "/node/{node_id}/ont/{ont_id}/status",
    summary="Get ont status information",
    description="Exposed, needs data model.",
)
def get_ont_status(request: Request, node_id: str, ont_id: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_status(node_id, ont_id)  # todo process reply


@router.get(
    "/node/{node_id}/ont/{ont_id}/errors",
    summary="Get ont pon pm statistics",
    description="Exposed, needs data model. Gets the pon pm data on an ont and returns them as a set of lists "
    "ordered from most recent to oldest. Can return intervals of 1-day or 15-min with the optional "
    "parameter interval. If the interval is 1-day count must be at mose 8, if the interval is "
    "15-min it must be at most 96.",
)
def get_ont_errors(
    request: Request, node_id: str, ont_id: int, interval: str = "1-day", count: int = 8
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    return cms.get_ont_errors(
        node_id, ont_id, interval=interval, count=count
    )  # todo input validation


@router.delete(
    "/node/{node_id}/ont/{ont_id}/errors",
    summary="Clears ont pon pm statistics",
    description="Exposed, needs data model. Resets the pon pm data on an ont to 0s for the configured selection. The "
    "default is the last day. Can clear intervals of 1-day or 15-min with the optional parameter interval. If the "
    "interval is 1-day count must be at mose 8, if the interval is 15-min it must be at most 96.",
)
def clear_ont_errors(
    request: Request, node_id: str, ont_id: int, interval: str = "1-day", count: int = 1
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    success = cms.clear_ont_errors(node_id, ont_id, interval=interval, count=count)
    if not success:
        raise HTTPException(500, detail="CMS server returned an error")


# <---------------------------------------------------------------------------------------------------------- ONT Ports


@router.get(
    "/node/{node_id}/ont/{ont_id}/port",
    summary="List all ports on ont",
    description="Lists all of the ports on the ont that meet the port_type filter. If the filter is left blank it will "
    "return all ports. Any of the following ports are valid: rg, fb, ge, fe, hpna, voice, ds1, avo, videorf, videohotrf."
    " Multiple types may be provided as a comma separated list.",
)
def list_ont_ports(
    request: Request,
    node_id: str,
    ont_id: int,
    port_type: str = "",
):
    port_type_table = {
        "rg": "OntRg",
        "fb": "OntFb",
        "ge": "OntEthGe",
        "fe": "OntEthFe",
        "hpna": "OntEthHpna",
        "voice": "OntPots",
        "ds1": "OntDs1",
        "avo": "OntRfAvo",
        "videorf": "OntVideoRf",
        "videohotrf": "OntVideoHotRf",
    }

    port_type = port_type.replace(" ", "").split(",")
    port_types = []
    if port_type == [""]:
        port_types.extend(list(port_type_table.values()))
    else:
        for port_type in port_type:
            if port_type in port_type_table:
                port_types.append(port_type_table[port_type])
            else:
                raise HTTPException(422, f"Invalid port type: {port_type}")

    cms: CmsClient = request.app.state.cms
    return cms.list_ont_ports(node_id, ont_id, port_types=port_types)


# <------------------------------------------------------------------------------------------------------------- ONT GE


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/location",
    summary="Get all location information for a GE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_ge_port_location(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntEthGe", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/status",
    summary="Get all status information for a GE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_ge_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntEthGe", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/leases",
    summary="Get all lease information for a GE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_ge_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_leases(node_id, ont_id, "OntEthGe", port_nr)


@router.delete(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/leases",
    summary="Clear all leases on a GE port on an ont",
    description="Exposed, needs data model.",
)
def clear_ont_ge_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    leases = cms.get_ont_port_leases(node_id, ont_id, "OntEthGe", port_nr)
    reply = {}
    for lease in leases:
        ip = lease["entry"]["ip"]
        mac = lease["entry"]["mac"]
        success = cms.delete_lease(node_id, ip, mac)
        reply[ip] = "Clear" if success else "Fail"
    return reply


# <------------------------------------------------------------------------------------------------------------- ONT FE


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/fe/{port_nr}/location",
    summary="Get all location information for a FE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_fe_port_location(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntEthFe", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/fe/{port_nr}/status",
    summary="Get all status information for a FE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_fe_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntEthFe", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/fe/{port_nr}/leases",
    summary="Get all lease information for a FE port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_fe_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_leases(node_id, ont_id, "OntEthFe", port_nr)


@router.delete(
    "/node/{node_id}/ont/{ont_id}/port/fe/{port_nr}/leases",
    summary="Clear all leases on a FE port on an ont",
    description="Exposed, needs data model.",
)
def clear_ont_fe_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    leases = cms.get_ont_port_leases(node_id, ont_id, "OntEthFe", port_nr)
    reply = {}
    for lease in leases:
        ip = lease["entry"]["ip"]
        mac = lease["entry"]["mac"]
        success = cms.delete_lease(node_id, ip, mac)
        reply[ip] = "Clear" if success else "Fail"
    return reply


# <------------------------------------------------------------------------------------------------------------- ONT RG


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/rg/{port_nr}/location",
    summary="Get all location information for a RG port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_rg_port_location(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntRg", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/rg/{port_nr}/status",
    summary="Get all status information for a RG port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_rg_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntRg", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/rg/{port_nr}/leases",
    summary="Get all lease information for a RG port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_rg_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_leases(node_id, ont_id, "OntRg", port_nr)


@router.delete(
    "/node/{node_id}/ont/{ont_id}/port/rg/{port_nr}/leases",
    summary="Clear all leases on a RG port on an ont",
    description="Exposed, needs data model.",
)
def clear_ont_rg_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    leases = cms.get_ont_port_leases(node_id, ont_id, "OntRg", port_nr)
    reply = {}
    for lease in leases:
        ip = lease["entry"]["ip"]
        mac = lease["entry"]["mac"]
        success = cms.delete_lease(node_id, ip, mac)
        reply[ip] = "Clear" if success else "Fail"
    return reply


# <---------------------------------------------------------------------------------------------------------- ONT Voice


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/voice/{port_nr}/location",
    summary="Get all location information for a voice port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_voice_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntPots", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/voice/{port_nr}/status",
    summary="Get all status information for a voice port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_voice_port_status(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntPots", port_nr)


# <------------------------------------------------------------------------------------------------------------- ONT FB


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/fb/{port_nr}/location",
    summary="Get all location information for a FB port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_fb_port_location(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntFb", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/fb/{port_nr}/status",
    summary="Get all status information for a FB port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_fb_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntFb", port_nr)


# <------------------------------------------------------------------------------------------------------- ONT ETH HPNA


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/hpna/{port_nr}/location",
    summary="Get all location information for a HPNA port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_hpna_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntEthHpna", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/hpna/{port_nr}/status",
    summary="Get all status information for a HPNA port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_hpna_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntEthHpna", port_nr)


# <------------------------------------------------------------------------------------------------------------ ONT DS1


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ds1/{port_nr}/location",
    summary="Get all location information for a DS1 port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_ds1_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntDs1", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ds1/{port_nr}/status",
    summary="Get all status information for a DS1 port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_ds1_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntDs1", port_nr)


# <--------------------------------------------------------------------------------------------------------- ONT RF AVO


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/rfavo/{port_nr}/location",
    summary="Get all location information for a RF AVO port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_rfavo_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntRfAvo", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/rfavo/{port_nr}/status",
    summary="Get all status information for a RF AVO port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_rfavo_port_status(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntRfAvo", port_nr)


# <------------------------------------------------------------------------------------------------------- ONT VIDEO RF


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/videorf/{port_nr}/location",
    summary="Get all location information for a VIDEO RF port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_videorf_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntVideoRf", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/videorf/{port_nr}/status",
    summary="Get all status information for a VIDEO RF port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_videorf_port_status(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntVideoRf", port_nr)


# <--------------------------------------------------------------------------------------------------- ONT VIDEO HOT RF


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/videohotrf/{port_nr}/location",
    summary="Get all location information for a VIDEO HOT RF port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_videohotrf_port_location(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_location(node_id, ont_id, "OntVideoHotRf", port_nr)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/videohotrf/{port_nr}/status",
    summary="Get all status information for a VIDEO HOT RF port on an ont",
    description="Exposed, needs data model.",
)
def get_ont_videohotrf_port_status(
    request: Request, node_id: str, ont_id: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_port_status(node_id, ont_id, "OntVideoHotRf", port_nr)


# <--------------------------------------------------------------------------------------------------------------- XDSL


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}",
    summary="Lists all xdsl modems on a card",
    description="Exposed, needs data model.",
)
def list_xdsl_modems(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.list_card_xdsl(node_id, shelf_nr, card_nr)


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/provisioning",
    summary="Gets the provisioning info for an xdsl port",
    description="Exposed, needs data model.",
)
def get_xdsl_port_provisioning(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_port_provisioning(node_id, shelf_nr, card_nr, port_nr)


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/status",
    summary="Gets the provisioning info for an xdsl port",
    description="Exposed, needs data model.",
)
def get_xdsl_port_status(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_port_status(node_id, shelf_nr, card_nr, port_nr)


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/performance/eth",
    summary="Gets the performance stats for the modem's ethernet port",
    description="Exposed, needs data model. Gets the ethernet performance data on a modem and returns them as a set of "
    "lists ordered from most recent to oldest. Can return intervals of 1-day or 15-min with the optional "
    "parameter interval. If the interval is 1-day count must be at mose 8, if the interval is 15-min it "
    "must be at most 96.",
)
def get_xdsl_port_performance_eth(
    request: Request,
    node_id: str,
    shelf_nr: int,
    card_nr: int,
    port_nr: int,
    interval: str = "1-day",
    count: int = 8,
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_port_eth_performance(
        node_id, shelf_nr, card_nr, port_nr, interval=interval, count=count
    )


@router.delete(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/performance/eth",
    summary="Gets the performance stats for the modem's ethernet port",
    description="Exposed, needs data model. Resets the ethernet error data on a modem to 0s for the configured "
    "selection. The default is the last day. Can clear intervals of 1-day or 15-min with the optional parameter "
    "interval. If the interval is 1-day count must be at mose 8, if the interval is 15-min it must be at most 96.",
)
def clear_xdsl_port_performance_eth(
    request: Request,
    node_id: str,
    shelf_nr: int,
    card_nr: int,
    port_nr: int,
    interval: str = "1-day",
    count: int = 8,
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    return cms.clear_xdsl_port_eth_performance(
        node_id, shelf_nr, card_nr, port_nr, interval=interval, count=count
    )


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/performance/dsl",
    summary="Gets the performance stats for the modem's dsl port",
    description="Exposed, needs data model. Gets the dsl performance data on a modem and returns them as a set of "
    "lists ordered from most recent to oldest. Can return intervals of 1-day or 15-min with the optional "
    "parameter interval. If the interval is 1-day count must be at mose 8, if the interval is 15-min it "
    "must be at most 96.",
)
def get_xdsl_port_performance_dsl(
    request: Request,
    node_id: str,
    shelf_nr: int,
    card_nr: int,
    port_nr: int,
    interval: str = "1-day",
    count: int = 8,
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_port_dsl_performance(
        node_id, shelf_nr, card_nr, port_nr, interval=interval, count=count
    )


@router.delete(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/port/performance/dsl",
    summary="Gets the performance stats for the modem's ethernet port",
    description="Exposed, needs data model. Resets the dsl error data on a modem to 0s for the configured "
    "selection. The default is the last day. Can clear intervals of 1-day or 15-min with the optional parameter "
    "interval. If the interval is 1-day count must be at mose 8, if the interval is 15-min it must be at most 96.",
)
def clear_xdsl_port_performance_dsl(
    request: Request,
    node_id: str,
    shelf_nr: int,
    card_nr: int,
    port_nr: int,
    interval: str = "1-day",
    count: int = 8,
):
    if interval not in ["1-day", "15-min"]:
        raise HTTPException(
            422, detail=f"Interval must be '1-day' or '15-min', not '{interval}'"
        )

    if interval == "1-day" and count > 8:
        raise HTTPException(422, detail="Count must be at most 8 if interval is 1-day")

    if interval == "15-min" and count > 96:
        raise HTTPException(
            422, detail="Count must be at most 96 if interval is 15-min"
        )

    cms: CmsClient = request.app.state.cms
    return cms.clear_xdsl_port_dsl_performance(
        node_id, shelf_nr, card_nr, port_nr, interval=interval, count=count
    )


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/interface/provisioning",
    summary="Gets the associated interface info for an xdsl port",
    description="Exposed, needs data model.",
)
def get_xdsl_ai_provisioning(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_ai_provisioning(node_id, shelf_nr, card_nr, 200 + port_nr)


@router.get(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/interface/lease",
    summary="Gets the lease(s) on the associated interface for the modem",
    description="Exposed, needs data model.",
)
def get_xdsl_leases(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    return cms.get_xdsl_leases(node_id, shelf_nr, card_nr, 200 + port_nr)


@router.delete(
    "/node/{node_id}/xdsl/shelf/{shelf_nr}/card/{card_nr}/port/{port_nr}/interface/lease",
    summary="Deletes the leases on the associated interface for the modem",
    description="Exposed, needs data model.",
)
def clear_xdsl_leases(
    request: Request, node_id: str, shelf_nr: int, card_nr: int, port_nr: int
):
    cms: CmsClient = request.app.state.cms
    leases = cms.get_xdsl_leases(node_id, shelf_nr, card_nr, 200 + port_nr)
    reply = {}
    for lease in leases:
        ip = lease["entry"]["ip"]
        mac = lease["entry"]["mac"]
        success = cms.delete_lease(node_id, ip, mac)
        reply[ip] = "Clear" if success else "Fail"
    return reply


# <--------------------------------------------------------------------------------------------------------------- POTS


@router.get(
    "/node/{node_id}/pots/shelf/{shelf_nr}/card/{card_nr}",
    summary="Lists all pots ports on a card",
    description="Exposed, needs data model.",
)
def list_xdsl_pots(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    cms: CmsClient = request.app.state.cms
    return cms.list_card_pots(node_id, shelf_nr, 200 + card_nr)

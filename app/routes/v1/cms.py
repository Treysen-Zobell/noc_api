from fastapi import APIRouter, Request
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
    description="Exposed, needs data model",
)
def get_node_alarms(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.get_node_alarms(node_id)  # todo process reply


@router.get(
    "/node/{node_id}/shelf",
    summary="List all shelves on node",
    description="Feature not implemented",
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
    pass


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card",
    summary="List all cards on shelf",
    description="Feature not implemented",
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
    pass


@router.get(
    "/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon",
    summary="List all pons on card",
    description="Feature not implemented",
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
    pass


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
    description="Feature not implemented",
)
def list_node_onts(request: Request, node_id: str):
    cms: CmsClient = request.app.state.cms
    return cms.list_node_onts(node_id)


@router.get(
    "/node/{node_id}/ont/{ont_id}",
    summary="Get all ont information",
    description="Feature not implemented",
)
def get_ont(request: Request, node_id: str, ont_id: int):
    pass


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
    description="Exposed, needs data model",
)
def get_ont_status(request: Request, node_id: str, ont_id: int):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_status(node_id, ont_id)  # todo process reply


@router.get(
    "/node/{node_id}/ont/{ont_id}/errors",
    summary="Get ont pon pm statistics",
    description="Feature not implemented. Gets the pon pm data on an ont and returns them as a set of lists "
    "ordered from most recent to oldest. Can return intervals of 1-day or 15-min with the optional "
    "parameter interval. If the interval is 1-day count must be at mose 8, if the interval is "
    "15-min it must be at most 96.",
)
def get_ont_errors(
    request: Request, node_id: str, ont_id: int, interval: str = "1-day", count: int = 8
):
    cms: CmsClient = request.app.state.cms
    return cms.get_ont_errors(node_id, ont_id, interval=interval, count=count)


@router.delete(
    "/node/{node_id}/ont/{ont_id}/errors",
    summary="clears ont pon pm statistics",
    description="Feature not implemented. Resets the pon pm data on an ont to 0s for the configured selection. The "
    "default is the last day. Can clear intervals of 1-day or 15-min with the optional parameter interval. If the "
    "interval is 1-day count must be at mose 8, if the interval is 15-min it must be at most 96.",
)
def clear_ont_errors(
    request: Request, node_id: str, ont_id: int, interval: str = "1-day", count: int = 1
):
    cms: CmsClient = request.app.state.cms
    return cms.clear_ont_errors(node_id, ont_id, interval=interval, count=count)


@router.get(
    "/node/{node_id}/ont/{ont_id}/port",
    summary="List all ports on ont",
    description="Feature not implemented",
)
def list_ont_ports(request: Request, node_id: str, ont_id: int):
    pass


# <------------------------------------------------------------------------------------------------------------- ONT GE
# todo repeat for each port type


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}",
    summary="Get all information for a port on an ont",
    description="Feature not implemented",
)
def get_ont_port(request: Request, node_id: str, ont_id: int, port_nr: int):
    pass


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/location",
    summary="Get all location information for a port on an ont",
    description="Feature not implemented",
)
def get_ont_port_location(request: Request, node_id: str, ont_id: int, port_nr: int):
    pass


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}/status",
    summary="Get all status information for a port on an ont",
    description="Feature not implemented",
)
def get_ont_port_status(request: Request, node_id: str, ont_id: int, port_nr: int):
    pass


@router.get(
    "/node/{node_id}/ont/{ont_id}/port/ge/{port_nr}",
    summary="Get all lease information for a porn on an ont",
    description="Feature not implemented",
)
def get_ont_port_leases(request: Request, node_id: str, ont_id: int, port_nr: int):
    pass

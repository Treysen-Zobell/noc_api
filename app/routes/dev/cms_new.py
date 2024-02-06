from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/cms", tags=["cms"])


@router.get("/node", summary="List all nodes", description="Feature not implemented")
def list_nodes(request: Request):
    pass


@router.get("/node/{node_id}", summary="Get node information", description="Feature not implemented")
def get_node(request: Request, node_id: str):
    pass


@router.get("/node/{node_id}/shelf", summary="List all shelves on node", description="Feature not implemented")
def list_shelves(request: Request, node_id: str):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}", summary="Get shelf information", description="Feature not implemented")
def get_shelf(request: Request, node_id: str, shelf_nr: int):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}/card", summary="List all cards on shelf", description="Feature not implemented")
def list_shelves(request: Request, node_id: str, shelf_nr: int):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}", summary="Get card information", description="Feature not implemented")
def get_shelf(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon", summary="List all pons on card", description="Feature not implemented")
def list_shelves(request: Request, node_id: str, shelf_nr: int, card_nr: int):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon/{pon_nr}", summary="Get pon information", description="Feature not implemented")
def get_shelf(request: Request, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int):
    pass


@router.get("/node/{node_id}/shelf/{shelf_nr}/card/{card_nr}/pon/{pon_nr}/ont", summary="List all onts on pon", description="Feature not implemented")
def list_onts(request: Request, node_id: str, shelf_nr: int, card_nr: int, pon_nr: int):
    pass


@router.get("/node/{node_id}/ont/{ont_id}", summary="Get all ont information", description="Feature not implemented")
def get_ont(request: Request, node_id: str, ont_id: int):
    pass


@router.get("/node/{node_id}/ont/{ont_id}/location", summary="Get ont location information", description="Feature not implemented")
def get_ont_location(request: Request, node_id: str, ont_id: int):
    pass


@router.get("/node/{node_id}/ont/{ont_id}/status", summary="Get ont status information", description="Feature not implemented")
def get_ont_status(request: Request, node_id: str, ont_id: int):
    pass


@router.get("/node/{node_id}/ont/{ont_id}/errors",
            summary="Get ont pon pm statistics",
            description="Feature not implemented. Gets the bip errors on an ont and returns them as a set of lists "
                        "ordered from most recent to oldest. Can return intervals of 1-day or 15-min with the optional "
                        "parameter interval. If the interval is 1-day count must be at mose 8, if the interval is "
                        "15-min it must be at most 96.")
def get_ont_errors(request: Request, node_id: str, ont_id: int, interval: str = "1-day", count: int = 8):
    pass


@router.get("/node/{node_id}/ont/{ont_id}/port", summary="List all ports on ont", description="Feature not implemented")
def list_ont_ports(request: Request, node_id: str, ont_id: int):
    pass


@router.get("/node/{node_id}/ont/{ont_id}/port/{port_type}/{port_nr}", summary="List all ports on ont", description="Feature not implemented")
def get_ont_port(request: Request, node_id: str, ont_id: int):
    pass

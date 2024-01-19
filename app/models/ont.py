# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseModel

# Local App Imports


class OntGeneral(BaseModel):
    parent_node: str | None
    id: str | None
    admin_state: str | None
    model_nr: str | None
    serial_nr: str | None
    registration_id: str | None
    subscriber_id: str | None
    description: str | None
    vendor: str | None
    shelf: int | None
    card: int | None
    port: int | None
    pwe3prof: str | None
    low_rx_opt_pwr_ne_thresh: float | None
    high_rx_opt_pwr_ne_thresh: float | None
    us_sdber_rate: float | None
    low_rx_opt_pwr_fe_thresh: float | None
    high_rx_opt_pwr_fe_thresh: float | None
    low_tx_opt_pwr_thresh: float | None
    high_tx_opt_pwr_thresh: float | None
    low_laser_bias_thresh: float | None
    high_laser_bias_thresh: float | None
    low_line_pwr_feed_thresh: float | None
    high_line_pwr_feed_thresh: float | None
    low_ont_temp_thresh: float | None
    high_ont_temp_thresh: float | None
    battery_present: float | None
    pse_max_power_budget: int | None
    poe_class_control: str | None
    ont_port_color: int | None


class OntStatus(OntGeneral):
    operational_status: str | None
    critical_alarm_count: int | None
    major_alarm_count: int | None
    minor_alarm_count: int | None
    warning_alarm_count: int | None
    info_alarm_count: int | None
    derived_states: str | None
    clei: str | None
    product_code: str | None
    mfg_serial_number: str | None
    uptime: int | None
    rx_opt_signal_level: float | None
    tx_opt_signal_level: float | None
    loop_length: int | None
    fe_opt_signal_level: float | None
    ds_sdber_rate: float | None
    current_software_version: str | None
    alternate_software_version: str | None
    current_committed: bool | None
    rg_config_file_version: str | None
    voip_config_file_version: str | None
    current_customer_version: str | None
    alternate_customer_version: str | None
    onu_mac_address: str | None
    mta_mac_address: str | None
    response_time: int | None
    pse_available_power_budget: float | None
    pse_available_output_power: float | None
    pse_management_capability: str | None
    option: int | None


class OntPerformance(BaseModel):
    parent_node: str | None
    id: str | None
    bip_errors_up: int | None
    bip_errors_down: int | None
    bip_errored_seconds_up: int | None
    bip_errored_seconds_down: int | None
    bip_severely_errored_seconds_up: int | None
    bip_severely_errored_seconds_down: int | None
    bip_unavailable_seconds_up: int | None
    bip_unavailable_seconds_down: int | None
    missed_bursts_up: int | None
    missed_bursts_seconds: int | None
    gem_hec_errors_up: int | None


class OntPort(BaseModel):
    parent_node: str | None
    id: str | None
    slot: int | None
    port_number: int | None
    admin: str | None
    subscriber_id: str | None
    description: str | None
    speed: str | None
    duplex: str | None
    disable_on_battery: bool | None
    link_oam_events: str | None
    accept_link_oam: str | None
    accept_link_oam_loopbacks: str | None
    intf: str | None
    dhcp_limit_override: str | None
    downstream_bandwidth_profile: str | None
    force_dot1x: str | None
    role: str | None
    policing: str | None
    poe_power_priority: str | None
    poe_class_control: str | None
    voice_policy_profile: str | None
    ppte_power_control: str | None
    ont_port_color: str | None


class OntService(BaseModel):
    parent_node: str | None
    id: str | None
    port_number: int | None
    admin: str | None
    description: str | None
    service_name: str | None
    service_text: str | None
    bandwidth_name: str | None
    bandwidth_text: str | None
    bandwidth_id: str | None
    out_tag: str | None
    in_tag: str | None
    mcast_profile: str | None
    pon_cos: str | None
    upstream_cir_override: str | None
    upstream_pir_override: str | None
    downstream_pir_override: str | None
    hot_swap: bool | None
    pppoe_force_discard: bool | None


class OntVoice(BaseModel):
    parent_node: str | None
    id: str | None
    port_number: int | None
    admin: str | None
    subscriber_id: str | None
    description: str | None
    impedance: str | None
    signal_type: str | None
    system_tx_loss: str | None
    system_rx_loss: str | None
    tx_gain_2db: float | None
    rx_gain_2db: float | None
    nfpa_timer: int | None
    nfpa_timer_trig: bool | None


class OntList(BaseModel):
    onts: List[str]
    ont_count: int


class OntAction(BaseModel):
    success: bool
    additional_info: str

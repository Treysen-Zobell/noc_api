# Standard Library Imports
from typing import List

# Third Party Imports
from pydantic import BaseModel

# Local App Imports


class ModemInterface(BaseModel):
    parent_node: str | None
    shelf: int | None
    card: int | None
    interface: int | None
    name: str | None
    admin: str | None
    role: str | None
    description: str | None
    rstp_act: str | None
    rstp_priority: int | None
    rstp_path_cost: int | None
    rstp_edge: bool | None
    policy_map: str | None
    mtu: int | None
    exp_eth: str | None
    native_vlan: str | None
    split_hor: bool | None
    bpdu_mac: str | None
    lacp_tunnel: bool | None
    trusted: bool | None
    bpdu_guard: bool | None
    igmp_immed_leave: str | None
    sec_profile_name: str | None
    sec_profile_text: str | None
    pbit_name: str | None
    pbit_text: str | None
    subscriber_id: str | None
    iqa_mode: str | None
    iqa_poll_interval_seconds: int | None
    iqa_errors_per_million_threshold: int | None
    iqa_poll_window: int | None
    iqa_interval_count_alarm_threshold: int | None
    iqa_minimum_frame_count: int | None
    force_dot1x: str | None
    source_mac_limit: int | None


class ModemPort(BaseModel):
    parent_node: str | None
    shelf: int | None
    card: int | None
    interface: int | None
    admin: str | None
    description: str | None
    dsl_port_gos: int | None
    ethernet_port_gos: int | None
    service_type: str | None
    path_l: str | None
    fb_vpi: str | None
    fb_vci: str | None
    vsdl_prof: str | None
    rpt_events: bool | None
    power_save: bool | None
    power_down_timeout: int | None
    dmn: int | None
    dmx: int | None
    umn: int | None
    umx: int | None
    dmni: str | None
    umni: str | None
    dimxl: str | None
    uimxl: str | None
    dmns: int | None
    dmxs: int | None
    dts: int | None
    umns: int | None
    umxs: int | None
    uts: int | None
    po: str | None
    drm: str | None
    urm: str | None
    ddam: int | None
    duam: int | None
    udam: int | None
    uuam: int | None
    ddat: int | None
    duat: int | None
    udat: int | None
    uuat: int | None
    dei: str | None
    uei: str | None
    ahc: bool | None
    dgmne: int | None
    usmne: int | None
    dgmxn: int | None
    usmxn: int | None
    dgmxd: int | None
    ugmxd: int | None
    dgmns: int | None
    ugmns: int | None
    dgsr: int | None
    ugsr: int | None
    dgmnr: int | None
    usmnr: int | None
    gdir: str | None
    usir: str | None
    m: str | None
    u1a: int | None
    u1b: int | None
    u2a: int | None
    u2b: int | None
    u3a: int | None
    u3b: int | None
    u4a: int | None
    u4b: int | None
    ukl0: str | None
    d1i: int | None
    d1v: int | None
    d2i: int | None
    d2v: int | None
    d3i: int | None
    d3v: int | None
    d4i: int | None
    d4v: int | None
    d5i: int | None
    d5v: int | None
    d6i: int | None
    d6v: int | None
    d7i: int | None
    d7v: int | None
    d8i: int | None
    d8v: int | None
    d9i: int | None
    d9v: int | None
    d10i: int | None
    d10v: int | None
    d11i: int | None
    d11v: int | None
    d12i: int | None
    d12v: int | None
    d13i: int | None
    d13v: int | None
    d14i: int | None
    d14v: int | None
    d15i: int | None
    d15v: int | None
    d16i: int | None
    d16v: int | None
    desel: int | None
    descma: int | None
    descmb: int | None
    descmc: int | None
    dmus: int | None
    dfmin: int | None
    dfmax: int | None
    r1a: int | None
    r1b: int | None
    r2a: int | None
    r2b: int | None
    r3a: int | None
    r3b: int | None
    r4a: int | None
    r4b: int | None
    r5a: int | None
    r5b: int | None
    r6a: int | None
    r6b: int | None
    r7a: int | None
    r7b: int | None
    r8a: int | None
    r8b: int | None
    r9a: int | None
    r9b: int | None
    r10a: int | None
    r10b: int | None
    r11a: int | None
    r11b: int | None
    r12a: int | None
    r12b: int | None
    r13a: int | None
    r13b: int | None
    r14a: int | None
    r14b: int | None
    r15a: int | None
    r15b: int | None
    r16a: int | None
    r16b: int | None
    g1a: int | None
    g1b: int | None
    g2a: int | None
    g2b: int | None
    g3a: int | None
    g3b: int | None
    g4a: int | None
    g4b: int | None
    downstream_vectoring: str | None
    upstream_vectoring: str | None
    vectoring_group: str | None
    join_vectoring_group: bool | None


class Modem(BaseModel):
    port: ModemPort
    associated_interface: ModemInterface


class ModemStatus(BaseModel):
    parent_node: str | None
    shelf: int | None
    card: int | None
    interface: int | None
    operational_status: str | None
    derived_states: str | None
    operation: str | None
    mode: str | None
    active_profile: str | None
    last_retrain_status: str | None
    data_mode: str | None
    uptime: int | None
    atm_header_compression: str | None
    retrain_count: int | None
    last_applied_template: str | None
    act_vec_mode: str | None
    vec_state: str | None
    power_save_timer: int | None
    act_psd_mask: str | None
    upstream_rate: int | None
    upstream_delay: int | None
    upstream_inp: int | None
    upstream_snrm: int | None
    upstream_la: int | None
    upstream_attainable_rate: int | None
    upstream_atp: int | None
    upstream_atmptm: str | None
    upstream_enh_inp: str | None
    upstream_rtx_etr: int | None
    upstream_rtx_inp_shine: int | None
    upstream_rtx_inp_rein: int | None
    upstream_rtx_delay: int | None
    downstream_rate: int | None
    downstream_delay: int | None
    downstream_inp: int | None
    downstream_snrm: int | None
    downstream_la: int | None
    downstream_attainable_rate: int | None
    downstream_atp: int | None
    downstream_atmptm: str | None
    downstream_enh_inp: str | None
    downstream_rtx_etr: int | None
    downstream_rtx_inp_shine: int | None
    downstream_rtx_inp_rein: int | None
    downstream_rtx_delay: int | None


class ModemPerformance(BaseModel):
    parent_node: str | None
    shelf: int | None
    card: int | None
    interface: int | None
    code_violations: int | None
    code_violations_far_end: int | None
    forward_error_correction: int | None
    forward_error_correction_far_end: int | None
    forward_error_correction_seconds: int | None
    forward_error_correction_seconds_far_end: int | None
    errored_seconds: int | None
    errored_seconds_far_end: int | None
    severely_errored_seconds: int | None
    severely_errored_seconds_far_end: int | None
    loss_of_signal_seconds: int | None
    loss_of_signal_seconds_far_end: int | None
    unavailable_seconds: int | None
    unavailable_seconds_far_end: int | None
    full_initialization_count: int | None
    failed_full_initialization_count: int | None
    ptm_tc_crc_error_count: int | None
    ptm_tc_code_violation_count: int | None


class ModemAction(BaseModel):
    success: bool
    additional_info: str


class XDSLLineTest(BaseModel):
    parent_node: str | None
    shelf: int | None
    card: int | None
    interface: int | None
    execution_status: str | None
    result_summary: str | None
    hazard_potential: str | None
    foreign_emf: str | None
    resistive_faults: str | None
    receiver_off_hook: str | None
    ringer: str | None
    tip_ground_dc_volt: float | None
    ring_ground_dc_volt: float | None
    tip_ground_ac_volt: float | None
    ring_ground_ac_volt: float | None
    tip_ground_dc_ohm: int | None
    ring_ground_dc_ohm: int | None
    ringer_equivalent: float | None
    tip_ground_cap: float | None
    ring_ground_cap: float | None
    tip_ring_cap: float | None


class NodeAlarms(BaseModel):
    # todo Alarm format is not standardized
    alarms: List[dict]

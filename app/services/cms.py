# Standard Library Imports
import json
import random

# Third Party Imports
import requests
import xmltodict
from pydash.objects import get

# Local App Imports
from app.services.exceptions import (
    CmsAuthenticationFailure,
    CmsCommunicationFailure,
    CmsDeauthenticationFailure,
)
from app.models.v1.cms.modem import (
    ModemInterface,
    ModemPort,
    ModemPerformance,
    ModemStatus,
    XDSLLineTest,
    NodeAlarms,
)
from app.models.v1.cms.ont import (
    OntGeneral,
    OntStatus,
    OntPerformance,
    OntPort,
    OntService,
    OntVoice,
    OntList,
)
from app.services.environment import CMS_IP, CMS_PASSWORD, CMS_USERNAME


class CmsClient:
    def __init__(self):
        self.netconf_url = self.generate_netconf_url(CMS_IP)
        self.session_id = None

    # --- Authentication ---
    def login(self, username=CMS_USERNAME, password=CMS_PASSWORD) -> str:
        """
        Sends a login to request to the CMS server. Uses the ip, username, and password from the environment variables
        CMS_IP, CMS_USERNAME, and CMS_PASSWORD.
        :return: A CMS session ID used to authenticate additional requests.
        :raises: CmsCommunicationFailure if it is unable to reach the CMS server.
        :raises: CmsAuthenticationFailure if the CMS server denies the authentication process.
        """
        # Send login request
        payload = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <auth message-id="{self.message_id}">
                <login>
                    <UserName>{username}</UserName>
                    <Password>{password}</Password>
                </login>
            </auth>
            </soapenv:Body>
            </soapenv:Envelope>"""
        resp, _ = self.__post(payload)

        if resp == {}:
            raise CmsCommunicationFailure(self.netconf_url)

        code = get(resp, "Envelope.Body.auth-reply.ResultCode")
        session_id = get(resp, "Envelope.Body.auth-reply.SessionId")

        if session_id is None or code != "0":
            raise CmsAuthenticationFailure(CMS_USERNAME, CMS_IP)

        # Return valid session id
        self.session_id = session_id
        return session_id

    def logout(self) -> None:
        """
        Sends a logout request to the CMS server using the session id from the login request and the CMS server ip from
        the environment variable CMS_IP.
        :return: None
        :raises: CmsCommunicationFailure if it is unable to reach the CMS server.
        :raises: CmsDeauthenticationFailure if the server rejects the logout request.
        """
        # Send logout request
        payload = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <auth message-id="{self.message_id}">
                <logout>
                    <UserName>{CMS_USERNAME}</UserName>
                    <SessionId>{self.session_id}</SessionId>
                </logout>
            </auth>
            </soapenv:Body>
            </soapenv:Envelope>"""
        resp, _ = self.__post(payload)

        if resp == {}:
            raise CmsCommunicationFailure(self.netconf_url)

        # Verify logout success
        code = get(resp, "Envelope.Body.auth-reply.ResultCode")

        if code != "0":
            raise CmsDeauthenticationFailure(CMS_USERNAME, CMS_IP)

    # ----- Fiber -----
    def get_ont(self, node_id: str, ont_id: str) -> OntGeneral:
        """
        Retrieves information about an ont, requires the node the ont is on and the ont's id.
        :param node_id: CMS node id excluding NTWK-. Ex: rsvt-pon-1.
        :param ont_id: The ont's id. Ex: 18331
        :return: OntGeneral
        """
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <get-config>
                    <source>
                        <running/>
                    </source>
                    <filter type="subtree">
                        <top>
                            <object>
                            <type>Ont</type>
                            <id>
                                <ont>{ont_id}</ont>
                            </id>
                            </object>
                        </top>
                    </filter>
                </get-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract information
        ont_info = OntGeneral(
            parent_node=node_id,
            id=ont_id,
            admin_state=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.admin"
            ),
            model_nr=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ontprof.id.ontprof.@name",
            ),
            serial_nr=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.serno"
            ),
            registration_id=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.reg-id"
            ),
            subscriber_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.subscr-id",
            ),
            description=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descr"
            ),
            vendor=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.vendor"
            ),
            shelf=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.linked-pon.id.shelf",
            ),
            card=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.linked-pon.id.card",
            ),
            port=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.linked-pon.id.gponport",
            ),
            pwe3prof=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.pwe3prof"
            ),
            low_rx_opt_pwr_ne_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-rx-opt-pwr-ne-thresh",
            ),
            high_rx_opt_pwr_ne_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-rx-opt-pwr-ne-thresh",
            ),
            us_sdber_rate=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-sdber-rate",
            ),
            low_rx_opt_pwr_fe_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-rx-opt-pwr-fe-thresh",
            ),
            high_rx_opt_pwr_fe_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-rx-opt-pwr-fe-thresh",
            ),
            low_tx_opt_pwr_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-tx-opt-pwr-thresh",
            ),
            high_tx_opt_pwr_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-tx-opt-pwr-thresh",
            ),
            low_laser_bias_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-laser-bias-thresh",
            ),
            high_laser_bias_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-laser-bias-thresh",
            ),
            low_line_pwr_feed_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-line-pwr-feed-thresh",
            ),
            high_line_pwr_feed_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-line-pwr-feed-thresh",
            ),
            low_ont_temp_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.low-ont-temp-thresh",
            ),
            high_ont_temp_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.high-ont-temp-thresh",
            ),
            battery_present=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.serno"
            )
            == "true",
            pse_max_power_budget=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.pse-max-power-budget",
            ),
            poe_class_control=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.poe-class-control",
            ),
            ont_port_color=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ont-port-color",
            ),
        )

        return ont_info

    def get_ont_status(self, node_id, ont_id) -> OntStatus:
        # Send soap request for ont realtime info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>show-ont</action-type>
                    <action-args>
                        <ont>
                            <type>Ont</type>
                            <id><ont>{ont_id}</ont></id>
                        </ont>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return OntStatus(
            parent_node=node_id,
            id=ont_id,
            admin_state=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.admin",
            ),
            model_nr=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.ontprof.id.ontprof.@name",
            ),
            serial_nr=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.serno",
            ),
            registration_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.reg-id",
            ),
            subscriber_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.subscr-id",
            ),
            description=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.descr",
            ),
            vendor=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.vendor",
            ),
            shelf=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.linked-pon.id.shelf",
            ),
            card=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.linked-pon.id.card",
            ),
            port=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.linked-pon.id.gponport",
            ),
            pwe3prof=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.pwe3prof",
            ),
            low_rx_opt_pwr_ne_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-rx-opt-pwr-ne-thresh",
            ),
            high_rx_opt_pwr_ne_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-rx-opt-pwr-ne-thresh",
            ),
            us_sdber_rate=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.us-sdber-rate",
            ),
            low_rx_opt_pwr_fe_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-rx-opt-pwr-fe-thresh",
            ),
            high_rx_opt_pwr_fe_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-rx-opt-pwr-fe-thresh",
            ),
            low_tx_opt_pwr_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-tx-opt-pwr-thresh",
            ),
            high_tx_opt_pwr_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-tx-opt-pwr-thresh",
            ),
            low_laser_bias_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-laser-bias-thresh",
            ),
            high_laser_bias_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-laser-bias-thresh",
            ),
            low_line_pwr_feed_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-line-pwr-feed-thresh",
            ),
            high_line_pwr_feed_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-line-pwr-feed-thresh",
            ),
            low_ont_temp_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.low-ont-temp-thresh",
            ),
            high_ont_temp_thresh=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.high-ont-temp-thresh",
            ),
            battery_present=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.serno",
            )
            == "true",
            pse_max_power_budget=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.pse-max-power-budget",
            ),
            poe_class_control=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.poe-class-control",
            ),
            ont_port_color=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get-config.object.ont-port-color",
            ),
            operational_status=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.op-stat",
            ),
            critical_alarm_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.crit",
            ),
            major_alarm_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.maj",
            ),
            minor_alarm_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.min",
            ),
            warning_alarm_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.warn",
            ),
            info_alarm_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.info",
            ),
            derived_states=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.derived-states",
            ),
            clei=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.clei",
            ),
            product_code=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.product-code",
            ),
            mfg_serial_number=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.mfg-serno",
            ),
            uptime=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.uptime",
            ),
            rx_opt_signal_level=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.opt-sig-lvl",
            ),
            tx_opt_signal_level=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.tx-opt-lvl",
            ),
            loop_length=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.range-length",
            ),
            fe_opt_signal_level=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.fe-opt-lvl",
            ),
            ds_sdber_rate=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.cur-ds-sdber-rate",
            ),
            current_software_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.curr-sw-vers",
            ),
            alternate_software_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.alt-sw-vers",
            ),
            current_committed="true"
            == get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.curr-cust-vers",
            ),
            rg_config_file_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.rg-file-vers",
            ),
            voip_config_file_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.voip-file-vers",
            ),
            current_customer_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.curr-cust-vers",
            ),
            alternate_customer_version=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.alt-cust-vers",
            ),
            onu_mac_address=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.onu-mac",
            ),
            mta_mac_address=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.mta-mac",
            ),
            response_time=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.response-time",
            ),
            pse_available_power_budget=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.pse-available-power-budget",
            ),
            pse_aggregate_output_power=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.pse-aggregate-output-power",
            ),
            pse_management_capability=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.pse-mgmt-capb",
            ),
            option=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match.get.object.option",
            ),
        )

    def get_ont_performance(self, node_id: str, ont_id: str) -> OntPerformance:
        # Send soap request for ont bip errors to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>show-ont-pm</action-type>
                    <action-args>
                        <object>
                            <type>Ont</type>
                            <id>
                                <ont>{ont_id}</ont>
                            </id>
                        </object>
                        <bin-type>1-day</bin-type>
                        <start-bin>1</start-bin>
                        <count>1</count>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract information
        bip_errors = {}
        error_types = get(
            resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.types"
        )
        error_values = get(
            resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.bin.val"
        )
        if isinstance(error_types, str) and isinstance(error_values, str):
            bip_errors = dict(zip(error_types.split(" "), error_values.split(" ")))

        return OntPerformance(
            parent_node=node_id,
            id=ont_id,
            bip_errors_up=get(bip_errors, "bip-err-up"),
            bip_errors_down=get(bip_errors, "bip-err-down"),
            bip_errored_seconds_up=get(bip_errors, "bip-err-sec-up"),
            bip_errored_seconds_down=get(bip_errors, "bip-err-sec-down"),
            bip_severely_errored_seconds_up=get(bip_errors, "bip-sev-err-sec-up"),
            bip_severely_errored_seconds_down=get(bip_errors, "bip-sev-err-sec-down"),
            bip_unavailable_seconds_up=get(bip_errors, "bip-unavail-sec-up"),
            bip_unavailable_seconds_down=get(bip_errors, "bip-unavail-sec-down"),
            missed_bursts_up=get(bip_errors, "miss-burst-up"),
            missed_bursts_seconds=get(bip_errors, "missed-burst-sec"),
            gem_hec_errors_up=get(bip_errors, "gem-hec-err-up"),
        )

    def get_ont_port(self, node_id: str, ont_id: str, port_nr: int) -> OntPort:
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <get-config>
                    <source>
                        <running/>
                    </source>
                    <filter type="subtree">
                        <top>
                            <object>
                            <type>OntEthGe</type>
                            <id>
                                <ont>{ont_id}</ont>
                                <ontslot>3</ontslot>
                                <ontethge>{port_nr}</ontethge>
                            </id>
                            </object>
                        </top>
                    </filter>
                </get-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return OntPort(
            parent_node=node_id,
            id=ont_id,
            slot=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.id.ontslot",
            ),
            port_number=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.id.ontethge",
            ),
            admin=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.admin"
            ),
            subscriber_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.subscr-id",
            ),
            description=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descr"
            ),
            speed=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.speed"
            ),
            duplex=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.duplex"
            ),
            disable_on_battery=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.disable-on-batt",
            )
            == "true",
            link_oam_events=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.link-oam-events",
            )
            == "true",
            accept_link_oam_loopbacks=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.accept-link-oam-loopbacks",
            )
            == "true",
            intf=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.intf"
            ),
            dhcp_limit_override=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dhcp-limit-override",
            ),
            downstream_bandwidth_profile=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-bw-prof",
            ),
            force_dot1x=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.force-dot1x",
            ),
            role=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.role"
            ),
            policing=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.policing"
            ),
            poe_power_priority=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.poe-power-priority",
            ),
            poe_class_control=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.poe-class-control",
            ),
            voice_policy_profile=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.voice-policy-profile",
            ),
            ppte_power_control=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ppte-power-control",
            )
            == "false",
            ont_port_color=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ont-port-color",
            ),
        )

    def get_ont_port_data_service(
        self, node_id: str, ont_id: str, port_nr: int
    ) -> OntService:
        # Send soap request for ont info to cms server
        payload = f"""
                    <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
                    <soapenv:Body>
                    <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                        <get-config>
                            <source>
                                <running/>
                            </source>
                            <filter type="subtree">
                                <top>
                                    <object>
                                    <type>OntEthGe</type>
                                    <id>
                                        <ont>{ont_id}</ont>
                                        <ontslot>3</ontslot>
                                        <ontethge>{port_nr}</ontethge>
                                    </id>
                                    <children>
                                        <type>EthSvc</type>
                                        <attr-list>admin descr tag-action bw-prof out-tag in-tag mcast-prof pon-cos us-cir-override us-pir-override ds-pir-override hot-swap pppoe-force-discard</attr-list>
                                    </children>
                                    </object>
                                </top>
                            </filter>
                        </get-config>
                    </rpc>
                    </soapenv:Body>
                    </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return OntService(
            parent_node=node_id,
            id=ont_id,
            port_number=port_nr,
            admin=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.admin",
            ),
            description=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.descr",
            ),
            service_name=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.id.ethsvc.@name",
            ),
            service_text=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.id.ethsvc.#text",
            ),
            bandwidth_name=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.bw-prof.id.bwprof.@name",
            ),
            bandwidth_text=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.bw-prof.id.bwprof.#text",
            ),
            bandwidth_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.bw-prof.id.bwprof.@localId",
            ),
            out_tag=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.out-tag",
            ),
            in_tag=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.in-tag",
            ),
            mcast_profile=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.mcast-prof",
            ),
            pon_cos=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.pon-cos",
            ),
            upstream_cir_override=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.us-cir-override",
            ),
            upstream_pir_override=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.us-pir-override",
            ),
            downstream_pir_override=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.ds-pir-override",
            ),
            hot_swap=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.hot-swap",
            )
            == "true",
            pppoe_force_discard=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child.pppoe-force-discard",
            )
            == "true",
        )

    def get_ont_voice_service(
        self, node_id: str, ont_id: str, port_nr: int
    ) -> OntVoice:
        # Send soap request for ont info to cms server
        payload = f"""
                    <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
                    <soapenv:Body>
                    <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                        <get-config>
                            <source>
                                <running/>
                            </source>
                            <filter type="subtree">
                                <top>
                                    <object>
                                    <type>OntPots</type>
                                    <id>
                                        <ont>{ont_id}</ont>
                                        <ontslot>6</ontslot>
                                        <ontpots>{port_nr}</ontpots>
                                    </id>
                                    </object>
                                </top>
                            </filter>
                        </get-config>
                    </rpc>
                    </soapenv:Body>
                    </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return OntVoice(
            parent_node=node_id,
            id=ont_id,
            port_number=port_nr,
            admin=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.admin"
            ),
            subscriber_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.subscr-id",
            ),
            description=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descr"
            ),
            impedance=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.impedance",
            ),
            signal_type=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.signal-type",
            ),
            system_tx_loss=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.system-tx-loss",
            ),
            system_rx_loss=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.system.rx-loss",
            ),
            tx_gain_2db=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.tx-gain-2db",
            ),
            rx_gain_2db=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rx-gain-2db",
            ),
            nfpa_timer=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.nfpa-timer",
            ),
            nfpa_timer_trig=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.nfpa-timer-trig",
            )
            == "true",
        )

    def list_onts_on_gpon(
        self, node_id: str, shelf_nr: int, card_nr: int, gpon_nr: int
    ) -> OntList:
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <get-config>
                    <source>
                        <running/>
                    </source>
                    <filter type="subtree">
                        <top>
                            <object>
                                <type>System</type>
                                <id/>
                                <children>
                                    <type>Ont</type>
                                    <attr-filter>
                                        <linked-pon>
                                            <type>GponPort</type>
                                            <id>
                                                <shelf>{shelf_nr}</shelf>
                                                <card>{card_nr}</card>
                                                <gponport>{gpon_nr}</gponport>
                                            </id>
                                        </linked-pon>
                                    </attr-filter>
                                </children>
                            </object>
                        </top>
                    </filter>
                </get-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Check if successful
        if (
            get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children"
            )
            is None
        ):
            return OntList(onts=[], count=-1)

        children = get(
            resp,
            "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child",
        )
        if not isinstance(children, list):
            children = [children]

        ont_ids = []
        for child in children:
            if get(child, "id.ont") is not None:
                ont_ids.append(get(child, "id.ont"))

        return OntList(onts=ont_ids, count=len(ont_ids))

    def reset_ont_performance(self, node_id: str, ont_id: str) -> bool:
        # Send soap request for ont bip errors to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>clear-ont-pm</action-type>
                    <action-args>
                        <object>
                            <type>Ont</type>
                            <id>
                                <ont>{ont_id}</ont>
                            </id>
                        </object>
                        <bin-type>1-day</bin-type>
                        <start-bin>1</start-bin>
                        <count>8</count>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def reset_ont(self, node_id: str, ont_id: str, force=True) -> bool:
        # Send request to reset ont
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>
                        reset-ont
                    </action-type>
                    <action-args>
                        <object>
                            <type>Ont</type>
                            <id>
                                <ont>{ont_id}</ont>
                            </id>
                        </object>
                        <force>{'true' if force else 'false'}</force>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def quarantine_ont(self, node_id: str, ont_serial_nr: str) -> bool:
        # Send request to add ont on node with serial number to quarantine pool
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object get-config="true" operation="create">
                                <type>QuarOnt</type>
                                <id>
                                    <quaront>CXNK{ont_serial_nr}</quaront>
                                </id>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def release_ont(self, node_id: str, ont_serial_nr: str) -> bool:
        # Send request to cms to add ont to quarantine pool
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="delete">
                                <type>QuarOnt</type>
                                <id>
                                    <quaront>CXNK{ont_serial_nr}</quaront>
                                </id>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def disable_ont(self, node_id: str, ont_id: str) -> bool:
        # Send soap request to cms to disable ont
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>Ont</type>
                                <id>
                                    <ont>{ont_id}</ont>
                                </id>
                                <admin>disabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def disable_ont_port(self, node_id: str, ont_id, port_nr: str) -> bool:
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>OntEthGe</type>
                                <id>
                                    <ont>{ont_id}</ont>
                                    <ontslot>3</ontslot>
                                    <ontethge>{port_nr}</ontethge>
                                </id>
                                <admin>disabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def enable_ont(self, node_id: str, ont_id: str) -> bool:
        # Send soap request to cms to disable ont
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>Ont</type>
                                <id>
                                    <ont>{ont_id}</ont>
                                </id>
                                <admin>enabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def enable_ont_port(self, node_id: str, ont_id: str, port_nr: str) -> bool:
        # Send soap request to cms to enable on port.
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>OntEthGe</type>
                                <id>
                                    <ont>{ont_id}</ont>
                                    <ontslot>3</ontslot>
                                    <ontethge>{port_nr}</ontethge>
                                </id>
                                <admin>enabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    # ------ DSL ------
    def get_xdsl_interface(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> ModemInterface:
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <get-config>
                    <source>
                        <running/>
                    </source>
                    <filter type="subtree">
                        <top>
                            <object>
                                <type>EthIntf</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <ethintf>{interface_id + 200}</ethintf>
                                </id>
                            </object>
                        </top>
                    </filter>
                </get-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return ModemInterface(
            parent_node=node_id,
            shelf=shelf_nr,
            card=card_nr,
            interface=interface_id,
            name=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.name"
            ),
            admin=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.admin"
            ),
            role=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.role"
            ),
            description=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.desc"
            ),
            rstp_act=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rstp-act"
            ),
            rstp_priority=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rstp-prio",
            ),
            rstp_path_cost=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rstp-path-cost",
            ),
            rstp_edge=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rstp-edge",
            )
            == "true",
            policy_map=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.policy-map",
            ),
            mtu=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.mtu"
            ),
            exp_eth=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.exp-eth"
            ),
            native_vlan=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.native-vlan",
            ),
            split_hor=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.split-hor",
            )
            == "true",
            bpdu_mac=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.bpdu-mac"
            ),
            lacp_tunnel=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.lacp-tunnel",
            )
            == "true",
            trusted=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.trusted"
            )
            == "true",
            bpdu_guard=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.bpdu-guard",
            )
            == "true",
            igmp_immed_leave=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.igmp-immed-leave",
            ),
            sec_profile_name=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.sec.id.ethsecprof.@name",
            ),
            sec_profile_text=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.sec.id.ethsecprof.#text",
            ),
            pbit_name=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.pbit-map.id.dscpmap.@name",
            ),
            pbit_text=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.pbit-map.id.dscpmap.#text",
            ),
            subscriber_id=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.subscr-id",
            ),
            iqa_mode=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-mode"
            ),
            iqa_poll_interval_seconds=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-poll-interval-sec",
            ),
            iqa_errors_per_million_threshold=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-err-per-million-thresh",
            ),
            iqa_poll_window=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-poll-window",
            ),
            iqa_interval_count_alarm_threshold=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-interval-cnt-alm-thresh",
            ),
            iqa_minimum_frame_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.iqa-min-frame-cnt",
            ),
            force_dot1x=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.force-dot1x",
            ),
            source_mac_limit=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.src-mac-limit",
            ),
        )

    def get_xdsl_port(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> ModemPort:
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <get-config>
                    <source>
                        <running/>
                    </source>
                    <filter type="subtree">
                        <top>
                            <object>
                                <type>DslPort</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <dslport>{interface_id}</dslport>
                                </id>
                            </object>
                        </top>
                    </filter>
                </get-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return ModemPort(
            parent_node=node_id,
            shelf=shelf_nr,
            card=card_nr,
            interface=interface_id,
            admin=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.admin"
            ),
            description=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.desc"
            ),
            dsl_port_gos=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.gos.id.dslportgos",
            ),
            ethernet_port_gos=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.eth-gos.id.ethportgos",
            ),
            service_type=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.svc-type"
            ),
            path_l=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.path-l"
            ),
            fb_vpi=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.fb-vpi"
            ),
            fb_vci=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.fb-vci"
            ),
            vsdl_prof=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.vdsl-prof",
            ),
            rpt_events=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.rpt-events",
            )
            == "true",
            power_save=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.power-save",
            )
            == "true",
            power_down_timeout=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.power-down-timeout",
            ),
            dmn=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmn"
            ),
            dmx=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmx"
            ),
            umn=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.umn"
            ),
            umx=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.umx"
            ),
            dmni=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmni"
            ),
            umni=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.umni"
            ),
            dimxl=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dimxl"
            ),
            uimxl=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.uimxl"
            ),
            dmns=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmns"
            ),
            dmxs=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmxs"
            ),
            dts=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dts"
            ),
            umns=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.umns"
            ),
            umxs=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.umxs"
            ),
            uts=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.uts"
            ),
            po=get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.po"),
            drm=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.drm"
            ),
            urm=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.urm"
            ),
            ddam=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ddam"
            ),
            duam=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.duam"
            ),
            udam=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.udam"
            ),
            uuam=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.uuam"
            ),
            ddat=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ddat"
            ),
            duat=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.duat"
            ),
            udat=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.udat"
            ),
            uuat=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.uuat"
            ),
            dei=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dei"
            ),
            uei=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.uei"
            ),
            ahc=get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ahc")
            == "true",
            dgmne=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgmne"
            ),
            usmne=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.usmne"
            ),
            dgmxn=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgmxn"
            ),
            usmxn=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.usmxn"
            ),
            dgmxd=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgmxd"
            ),
            ugmxd=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ugmxd"
            ),
            dgmns=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgmns"
            ),
            ugmns=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ugmns"
            ),
            dgsr=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgsr"
            ),
            ugsr=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ugsr"
            ),
            dgmnr=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dgmnr"
            ),
            usmnr=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.usmnr"
            ),
            gdir=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.gdir"
            ),
            usir=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.usir"
            ),
            m=get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.m"),
            u1a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u1a"
            ),
            u1b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u1b"
            ),
            u2a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u2a"
            ),
            u2b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u2b"
            ),
            u3a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u3a"
            ),
            u3b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u3b"
            ),
            u4a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u4a"
            ),
            u4b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.u4b"
            ),
            ukl0=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ukl0"
            ),
            d1i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d1i"
            ),
            d1v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d1v"
            ),
            d2i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d2i"
            ),
            d2v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d2v"
            ),
            d3i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d3i"
            ),
            d3v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d3v"
            ),
            d4i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d4i"
            ),
            d4v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d4v"
            ),
            d5i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d5i"
            ),
            d5v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d5v"
            ),
            d6i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d6i"
            ),
            d6v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d6v"
            ),
            d7i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d7i"
            ),
            d7v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d7v"
            ),
            d8i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d8i"
            ),
            d8v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d8v"
            ),
            d9i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d9i"
            ),
            d9v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d9v"
            ),
            d10i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d10i"
            ),
            d10v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d10v"
            ),
            d11i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d11i"
            ),
            d11v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d11v"
            ),
            d12i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d12i"
            ),
            d12v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d12v"
            ),
            d13i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d13i"
            ),
            d13v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d13v"
            ),
            d14i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d14i"
            ),
            d14v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d14v"
            ),
            d15i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d15i"
            ),
            d15v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d15v"
            ),
            d16i=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d16i"
            ),
            d16v=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.d16v"
            ),
            desel=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.desel"
            ),
            descma=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descma"
            ),
            descmb=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descmb"
            ),
            descmc=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.descmc"
            ),
            dmus=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dmus"
            ),
            dfmin=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dfmin"
            ),
            dfmax=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.dfmax"
            ),
            r1a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r1a"
            ),
            r1b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r1b"
            ),
            r2a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r2a"
            ),
            r2b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r2b"
            ),
            r3a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r3a"
            ),
            r3b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r3b"
            ),
            r4a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r4a"
            ),
            r4b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r4b"
            ),
            r5a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r5a"
            ),
            r5b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r5b"
            ),
            r6a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r6a"
            ),
            r6b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r6b"
            ),
            r7a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r7a"
            ),
            r7b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r7b"
            ),
            r8a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r8a"
            ),
            r8b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r8b"
            ),
            r9a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r9a"
            ),
            r9b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r9b"
            ),
            r10a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r10a"
            ),
            r10b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r10b"
            ),
            r11a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r11a"
            ),
            r11b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r11b"
            ),
            r12a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r12a"
            ),
            r12b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r12b"
            ),
            r13a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r13a"
            ),
            r13b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r13b"
            ),
            r14a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r14a"
            ),
            r14b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r14b"
            ),
            r15a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r15a"
            ),
            r15b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r15b"
            ),
            r16a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r16a"
            ),
            r16b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.r16b"
            ),
            g1a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g1a"
            ),
            g1b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g1b"
            ),
            g2a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g2a"
            ),
            g2b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g2b"
            ),
            g3a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g3a"
            ),
            g3b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g3b"
            ),
            g4a=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g4a"
            ),
            g4b=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.g4b"
            ),
            downstream_vectoring=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-vectoring",
            ),
            upstream_vectoring=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-vectoring",
            ),
            vectoring_group=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.vectoring-group",
            ),
            join_vectoring_group=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.join-vectoring-grp",
            )
            == "true",
        )

    def get_xdsl_status(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> ModemStatus:
        # Send soap request for ont info to cms server
        payload = f"""
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                    <soapenv:Body>
                    <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                        <get>
                            <filter type="subtree">
                                <top>
                                    <object>
                                        <type>DslPort</type>
                                        <id>
                                            <shelf>1</shelf>
                                            <card>1</card>
                                            <dslport>1</dslport>
                                        </id>
                                        <attr-list>op-stat derived-states op mode act init data-mode op-time ahc retrain-count last-templ act-vec-mode vec-state oper-status power-save-timer act-psd-mask us-rate us-delay us-inp us-snrm us-la us-att-rate us-atp us-atmptm us-enh-inp us-rtx-etr us-rtx-inp-shine us-rtx-inp-rein us-rtx-delay ds-rate ds-delay ds-inp ds-snrm ds-atten ds-att-rate ds-atp ds-atmptm ds-enh-inp ds-rtx-etr ds-rtx-inp-shine ds-rtx-inp-rein ds-rtx-delay </attr-list>
                                    </object>
                                </top>
                            </filter>
                        </get>
                    </rpc>
                    </soapenv:Body>
                    </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        return ModemStatus(
            parent_node=node_id,
            shelf=shelf_nr,
            card=card_nr,
            interface=interface_id,
            operational_status=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.op-stat"
            ),
            derived_states=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.derived-states",
            ),
            operation=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.op"
            ),
            mode=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.mode"
            ),
            active_profile=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.act"
            ),
            last_retrain_status=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.init"
            ),
            data_mode=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.data-mode",
            ),
            uptime=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.op-time"
            ),
            atm_header_compression=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ahc"
            ),
            retrain_count=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.retrain-count",
            ),
            last_applied_template=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.last-templ",
            ),
            act_vec_mode=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.act-vec-mode",
            ),
            vec_state=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.vec-state",
            ),
            power_save_timer=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.power-save-timer",
            ),
            act_psd_mask=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.act-psd-mask",
            ),
            upstream_rate=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-rate"
            ),
            upstream_delay=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-delay"
            ),
            upstream_inp=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-inp"
            ),
            upstream_snrm=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-snrm"
            ),
            upstream_la=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-la"
            ),
            upstream_attainable_rate=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-att-rate",
            ),
            upstream_atp=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-atp"
            ),
            upstream_atmptm=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-atmptm",
            ),
            upstream_enh_inp=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-enh-inp",
            ),
            upstream_rtx_etr=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-rtx-etr",
            ),
            upstream_rtx_inp_shine=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-rtx-inp-shine",
            ),
            upstream_rtx_inp_rein=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-rtx-inp-rein",
            ),
            upstream_rtx_delay=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.us-rtx-delay",
            ),
            downstream_rate=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-rate"
            ),
            downstream_delay=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-delay"
            ),
            downstream_inp=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-inp"
            ),
            downstream_snrm=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-snrm"
            ),
            downstream_la=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-la"
            ),
            downstream_attainable_rate=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-att-rate",
            ),
            downstream_atp=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-atp"
            ),
            downstream_atmptm=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-atmptm",
            ),
            downstream_enh_inp=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-enh-inp",
            ),
            downstream_rtx_etr=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-rtx-etr",
            ),
            downstream_rtx_inp_shine=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-rtx-inp-shine",
            ),
            downstream_rtx_inp_rein=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-rtx-inp-rein",
            ),
            downstream_rtx_delay=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.ds-rtx-delay",
            ),
        )

    def get_xdsl_performance(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> ModemPerformance:
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>show-dsl-pm</action-type>
                    <action-args>
                        <object>
                            <type>DslPort</type>
                            <id>
                                <shelf>{shelf_nr}</shelf>
                                <card>{card_nr}</card>
                                <dslport>{interface_id}</dslport>
                            </id>
                        </object>
                        <bin-type>1-day</bin-type>
                        <start-bin>1</start-bin>
                        <count>1</count>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        code_violations = {}
        error_types = get(
            resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.types"
        )
        error_values = get(
            resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.bin.val"
        )
        if isinstance(error_types, str) and isinstance(error_values, str):
            code_violations = dict(zip(error_types.split(" "), error_values.split(" ")))

        return ModemPerformance(
            parent_node=node_id,
            shelf=shelf_nr,
            card=card_nr,
            interface=interface_id,
            code_violations=get(code_violations, "cv-c"),
            code_violations_far_end=get(code_violations, "cv-cfe"),
            forward_error_correction=get(code_violations, "fec-c"),
            forward_error_correction_far_end=get(code_violations, "fec-cfe"),
            forward_error_correction_seconds=get(code_violations, "fec-l"),
            forward_error_correction_seconds_far_end=get(code_violations, "fec-lfe"),
            errored_seconds=get(code_violations, "es-l"),
            errored_seconds_far_end=get(code_violations, "es-lfe"),
            severely_errored_seconds=get(code_violations, "ses-l"),
            severely_errored_seconds_far_end=get(code_violations, "ses-lfe"),
            loss_of_signal_seconds=get(code_violations, "loss-l"),
            loss_of_signal_seconds_far_end=get(code_violations, "loss-lfe"),
            unavailable_seconds=get(code_violations, "uas-l"),
            unavailable_seconds_far_end=get(code_violations, "uas-lfe"),
            full_initialization_count=get(code_violations, "init-l"),
            failed_full_initialization_count=get(code_violations, "linit-l"),
            ptm_tc_crc_error_count=get(code_violations, "crc-p"),
            ptm_tc_code_violation_count=get(code_violations, "cv-p"),
        )

    def run_xdsl_line_test(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> XDSLLineTest:
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>test-pots-svc</action-type>
                    <action-args>
                        <pots>
                            <type>Pots</type>
                            <id>
                                <shelf>{shelf_nr}</shelf>
                                <card>{card_nr}</card>
                                <pots>{interface_id}</pots>
                            </id>
                        </pots>
                    </action-args>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload, timeout=30000)
        print(json.dumps(resp, indent=2))

        return XDSLLineTest(
            parent_node=node_id,
            shelf=shelf_nr,
            card=card_nr,
            interface=interface_id,
            execution_status=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.execution-status",
            ),
            result_summary=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.result-summary",
            ),
            hazard_potential=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.hazard-potential",
            ),
            foreign_emf=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.foreign-emf"
            ),
            resistive_faults=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.resistive-faults",
            ),
            receiver_off_hook=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.receiver-off-hook",
            ),
            ringer=get(
                resp, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ringer"
            ),
            tip_ground_dc_volt=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.tip-ground-dc-volt",
            ),
            ring_ground_dc_volt=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ring-ground-dc-volt",
            ),
            tip_ground_ac_volt=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.tip-ground-ac-volt",
            ),
            ring_ground_ac_volt=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ring-ground-ac-volt",
            ),
            tip_ground_dc_ohm=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.tip-ground-dc-ohm",
            ),
            ring_ground_dc_ohm=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ring-ground-dc-ohm",
            ),
            ringer_equivalent=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ringer-equiv",
            ),
            tip_ground_cap=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.tip-ground-cap",
            ),
            ring_ground_cap=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.ring-ground-cap",
            ),
            tip_ring_cap=get(
                resp,
                "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.tip-ring-cap",
            ),
        )

    def disable_xdsl_port(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> bool:
        # Send soap request to cms to disable xdsl port
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>DslPort</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <dslport>{interface_id}</dslport>
                                </id>
                                <admin>disabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def enable_xdsl_port(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> bool:
        # Send soap request to cms to enable xdsl port
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="www.w3.org/2003/05/soap-envelope">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>DslPort</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <dslport>{interface_id}</dslport>
                                </id>
                                <admin>enabled-no-alarms</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def enable_xdsl_bonding_group(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> bool:
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>DslBondIntf</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <dslbondintf>{interface_id}</dslbondintf>
                                </id>
                                <admin>enabled-no-alarms</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    def disable_xdsl_bonding_group(
        self, node_id: str, shelf_nr: int, card_nr: int, interface_id: int
    ) -> bool:
        # Send soap request for ont info to cms server
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <edit-config>
                    <target>
                        <running/>
                    </target>
                    <config>
                        <top>
                            <object operation="merge">
                                <type>DslBondIntf</type>
                                <id>
                                    <shelf>{shelf_nr}</shelf>
                                    <card>{card_nr}</card>
                                    <dslbondintf>{interface_id}</dslbondintf>
                                </id>
                                <admin>disabled</admin>
                            </object>
                        </top>
                    </config>
                </edit-config>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>"""

        resp, _ = self.__post(payload)

        # Extract success code
        if isinstance(get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply"), dict):
            return "ok" in get(resp, "soapenv:Envelope.soapenv:Body.rpc-reply")

        return False

    # ----- Node -----
    def get_node_alarms(self, node_id, _payload_after="<action-args/>") -> NodeAlarms:
        payload = f"""
            <soapenv:Envelope xmlns:soapenv=\"www.w3.org/2003/05/soap-envelope\">
            <soapenv:Body>
            <rpc message-id="{self.message_id}" nodename="NTWK-{node_id}" username="{CMS_USERNAME}" sessionid="{self.session_id}">
                <action>
                    <action-type>show-alarms</action-type>
                    <action-args/>
                </action>
            </rpc>
            </soapenv:Body>
            </soapenv:Envelope>
        """

        resp, more = self.__post(payload.replace("<action-args/>", _payload_after))

        alarms = get(
            resp,
            "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.alarm",
            default=[],
        )
        if isinstance(alarms, dict):
            alarms = [alarms]

        if more:
            object_type = f"<type>{alarms[-1]['object']['type']}</type>"
            object_id = ""
            for key, value in alarms[-1]["object"]["id"].items():
                object_id += f"<{key}>{value}</{key}>"
            last_alarm = f"<after-alarm>{alarms[-1]['alarm-type']}</after-alarm>"
            payload_insertion = f"<action-args><start-instance>{object_type}<id>{object_id}</id></start-instance>{last_alarm}</action-args>"

            return NodeAlarms(
                alarms=alarms
                + self.get_node_alarms(node_id, _payload_after=payload_insertion).alarms
            )

        return NodeAlarms(alarms=alarms)

    # ----- Utility -----
    @property
    def message_id(self):
        return str(random.getrandbits(random.randint(2, 31)))

    @property
    def headers(self):
        return {
            "Content-Type": "text/xml;charset=ISO8859-1",
            "User-Agent": f"CMS_NBI_CONNECT-{CMS_USERNAME}",
        }

    @staticmethod
    def generate_netconf_url(ip: str):
        return f"http://{ip}:18080/cmsexc/ex/netconf"

    def __post(self, payload: str, timeout: int = 5):
        try:
            resp = requests.post(
                url=self.netconf_url,
                headers=self.headers,
                data=payload,
                timeout=timeout,
            )
            data = xmltodict.parse(resp.content)

            return data, "<more/>" in str(resp.content)

        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.ConnectionError,
        ) as e:
            print(e)
            return [{}, False]

        except xmltodict.ParsingInterrupted as e:
            print(e)
            return [{}, False]

from volttron_installer.components.base_tile import BaseForm, BaseTab, BaseTile
from flet import *
from volttron_installer.modules.global_configs import global_hosts, find_dict_index
from volttron_installer.modules.global_event_bus import global_event_bus
from dataclasses import dataclass, field
import json

@dataclass
class Host(BaseTile):
    host_id: str
    ssh_sudo_user: str
    identity_file: str
    ssh_ip_address: str
    ssh_port: str

    host_tile: Container = field(init=False)
    def __post_init__(self):
        super().__init__(self.host_id)  # Initialize BaseTile with host_id
        self.host_tile = self.build_host_tile()

    def build_host_tile(self) -> Container:
        return self.build_tile()  # Calls BaseTile's build_tile method

class HostForm(BaseForm):
    def __init__(self, host, page: Page):
        self.host_id_field = TextField(on_change=self.validate_fields)
        self.ssh_sudo_user_field = TextField(on_change=self.validate_fields)
        self.identity_file_field = TextField(on_change=self.validate_fields)
        self.ssh_ip_address_field = TextField(on_change=self.validate_fields)
        self.ssh_port_field = TextField(on_change=self.validate_fields)
        form_fields = {
            "Host ID" : self.host_id_field,
            "SSH SUDO USER" : self.ssh_sudo_user_field,
            "Identity File" : self.identity_file_field,
            "SSH IP Address" : self.ssh_ip_address_field,
            "SSH Port" : self.ssh_port_field
        }
        self.key_constructor =[
            "host_id",
            "ssh_sudo_user",
            "identity_file",
            "ssh_ip_address",
            "ssh_port"
        ]

        super().__init__(page, form_fields)
        self.host: Host = host
        self.json_validity = True

    def save_config(self, e) -> None:
        # Save field values to host attributes
        self.host.ssh_sudo_user = self.ssh_sudo_user_field.value
        self.host.identity_file = self.identity_file_field.value
        self.host.ssh_ip_address = self.ssh_ip_address_field.value
        self.host.ssh_port = self.ssh_port_field.value

        # Save old name to a variable so we can see if it was originally in global_hosts
        old_name = self.host.host_id
        index = find_dict_index(global_hosts, old_name)

        # Now we can reassign new name
        self.host.host_id = self.host_id_field.value

        if index is not None:
            for key, val in zip(self.key_constructor, self.val_constructor):
                global_hosts[index][key] = val.value
        else:
            host_dictionary_appendable = {}
            for key, val in zip(self.key_constructor, self.val_constructor):
                host_dictionary_appendable[key] = val.value
            global_hosts.append(host_dictionary_appendable)

        self.host.host_tile.content.controls[0].value = self.host.host_id
        self.page.update()
        self.write_to_file("hosts", global_hosts)

class HostTab(BaseTab):
    def __init__(self, page: Page) -> None:
        self.list_of_hosts = Column(
            expand=2,
            controls=[
                OutlinedButton(text="Setup a Host", on_click=self.add_new_host)
            ]
        )
        super().__init__(self.list_of_hosts, page)
        self.page = page
        self.host_tab_view = self.tab

    #     global_event_bus.subscribe("tab_change", self.tab_change)

    # def tab_change(self, selected_tab):
    #     if selected_tab == 0:
    #         for host in global_agents:
    #             refreshed_agent = Host(
    #                                 agent_name = host["agent_name"],
    #                                 default_identity= host["default_identity"],
    #                                 agent_path= host["agent_path"],
    #                                 agent_configuration= host["agent_configuration"]
    #                             )
    #             refreshed_form = AgentForm(refreshed_agent, self.page)
    #             self.refresh_tiles(global_agents, refreshed_agent, refreshed_agent.agent_tile, refreshed_form, "agents")


    def add_new_host(self, e) -> None:
        self.add_new_tile(global_hosts, "hosts", Host, HostForm)

    def build_host_setup_tab(self) -> Container:
        return self.host_tab_view

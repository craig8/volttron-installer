from dataclasses import dataclass
from flet import *
from volttron_installer.modules.field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_hosts, find_dict_index
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.write_to_json import write_to_hosts

@dataclass
class Host:
    """Host object, will store nessary info and write to a file"""
    host_id: str
    ssh_sudo_user: str
    identity_file: str
    ssh_ip_address: str
    ssh_port: str # string for now

    def build_host_tile(self) -> Container:
        host_tile = build_default_tile(self.host_id)
        #host_tile.content.controls[1].on_click = self.remove_self
        return host_tile

class HostForm:
    def __init__(self, page: Page, host: Host, host_tile: Container):
        self.page = page
        self.host = host
        self.host_tile = host_tile

        self.host_id_field = TextField(on_change=self.validate_submit)
        self.ssh_sudo_user_field = TextField(on_change=self.validate_submit)
        self.identity_file_field = TextField(on_change=self.validate_submit)
        self.ssh_ip_address_field = TextField(on_change=self.validate_submit)
        self.ssh_port_field = TextField(on_change=self.validate_submit)
        self.formatted_fields: list = divide_fields([
                        field_pair("Host ID", self.host_id_field),
                        field_pair("SSH Sudo User", self.ssh_sudo_user_field),
                        field_pair("Identity File", self.identity_file_field),
                        field_pair("SSH IP Address", self.ssh_ip_address_field),
                        field_pair("SSH Port", self.ssh_port_field)
                        ])
        self.submit_button = OutlinedButton(text="Save", disabled=True, on_click=self.save_host_config)
        self._form = Column(
                        expand=3,
                        controls=[
                            *self.formatted_fields,
                            self.submit_button,
                        ]
                    )
        # On initialization, change on click
        self.host_tile.content.controls[1].on_click = self.remove_self

    def remove_self(self, e) -> None:
        index = find_dict_index(global_hosts, self.host.host_id)
        if index is not None:
            # Removes registered host from global hosts
            global_hosts.pop(index)  # Use pop(index) to remove by index
            writting_to_hosts()
        else:
            print("The host you are trying to remove hasnt even been properly registered yet.")
        # method to remove from parent container
        

    def save_host_config(self, e):
        self.host.ssh_sudo_user = self.ssh_sudo_user_field.value
        self.host.identity_file = self.identity_file_field.value
        self.host.ssh_ip_address = self.ssh_ip_address_field.value
        self.host.ssh_port = self.ssh_port_field.value

        # Save the old name of the host for checking purposes
        old_name = self.host.host_id

        # Run find host index function
        index = find_dict_index(global_hosts, old_name)

        # Now we can change
        self.host.host_id = self.host_id_field.value

        if index is not None:
            # Re-assign new name to agent and update agent details
            global_hosts[index]["host_id"] = self.host.host_id
            global_hosts[index]["ssh_sudo_user"] = self.host.ssh_sudo_user
            global_hosts[index]["identity_file"] = self.host.identity_file
            global_hosts[index]["ssh_ip_address"] = self.host.ssh_ip_address
            global_hosts[index]["ssh_port"] = self.host.ssh_port
        else:
            agent_dictionary_appendable = {
                "host_id": self.host.host_id,
                "ssh_sudo_user": self.host.ssh_sudo_user,
                "identity_file": self.host.identity_file,
                "ssh_ip_address": self.host.ssh_ip_address,
                "ssh_port": self.host.ssh_port,
            }
            global_hosts.append(agent_dictionary_appendable)
        self.host_tile.content.controls[0].value = self.host.host_id
        print(global_hosts) # Debug print
        self.host_tile.content.controls[0].value = self.host.host_id
        self.page.update() 
        writting_to_hosts()

    def validate_submit(self, e)-> None:
        if (
            self.host_id_field.value and
            self.ssh_ip_address_field.value and
            self.ssh_port_field.value and
            self.identity_file_field.value and
            self.ssh_sudo_user_field.value != ""
        ):
            self.submit_button.disabled = False
        else:
            self.submit_button.disabled = True
        self.submit_button.update()
    
    def build_host_form(self) -> Column:
        return self._form


class HostTab:
    def __init__(self, page: Page) -> None:
        self.page = page

        self.placeholder=Column(
            expand=3
        )
        self.list_of_hosts = Column(
                                scroll=ScrollMode.ADAPTIVE,
                                expand=2,
                                controls=[
                                    OutlinedButton(text="Create a new host", on_click=self.add_new_host)
                                ]
                            )
        self.host_tab_view=Container(
                                padding=padding.only(left=10),
                                margin=margin.only(left=10, right=10, bottom=5, top=5),
                                bgcolor="#20f4f4f4",
                                border_radius=12,
                                content=Row(
                                    controls=[
                                        self.list_of_hosts,
                                        VerticalDivider(color="white", width=9, thickness=3),
                                        self.placeholder
                                    ]
                                )
                            ) 

    def add_new_host(self, e) -> None:
        new_host = Host(
                host_id="New Host",
                ssh_sudo_user="",
                identity_file="",
                ssh_ip_address="",
                ssh_port="",
                
            )
        host_tile = new_host.build_host_tile()
        host_form = HostForm(self.page, new_host, host_tile)
        host_tile.on_click=lambda e: self.host_is_selected(e, host_form, host_tile)
        self.list_of_hosts.controls.append(host_tile)
        self.list_of_hosts.update()

    def host_is_selected(self, e, host_form: HostForm, host_tile: Container) -> None:
        self.host_tab_view.content.controls[2] = host_form.build_host_form()
        self.page.update()

    def build_hosts_tab(self)-> Container:
        return self.host_tab_view

# Im lazy...
def writting_to_hosts() -> None : write_to_hosts(global_hosts)
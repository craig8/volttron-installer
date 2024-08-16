from dataclasses import dataclass, field
from flet import *
from volttron_installer.modules.create_field_methods import field_pair, divide_fields
from volttron_installer.modules.global_configs import global_hosts, find_dict_index
from volttron_installer.components.default_tile_styles import build_default_tile
from volttron_installer.modules.write_to_json import write_to_hosts
from volttron_installer.modules.remove_from_controls import remove_from_selection
from volttron_installer.modules.global_event_bus import global_event_bus

@dataclass
class Host:
    """
    A class representing an individual Host for configuration.

    Attributes:
        host_id (str): The ID of the host.
        ssh_sudo_user (str): The SSH sudo user name.
        identity_file (str): The path to the SSH identity file.
        ssh_ip_address (str): The IP address of the host.
        ssh_port (str): The SSH port to connect to.
        id_key (int): A unique identifier key for the host_tile.
    """
    counter = 0

    host_id: str
    ssh_sudo_user: str
    identity_file: str
    ssh_ip_address: str
    ssh_port: str  # string for now

    id_key: int = field(init=False)

    def __post_init__(self):
        """
        Post-initialization to set the id_key and increment the counter.
        """
        self.id_key = Host.counter
        Host.counter += 1
        print("current id counter: ", self.id_key)

    def build_host_tile(self) -> Container:
        host_tile = build_default_tile(self.host_id)
        host_tile.key = self.id_key
        return host_tile

class HostForm:
    """
    A class to handle the form template for host registration and management.

    Attributes:
        page (Page): The Flet page where the components are rendered.
        host (Host): The host being handled by the form.
        host_tile (Container): The host tile container on the UI.
        list_of_hosts (Column): A Flet column containing the list of hosts.
        host_form_view (Container): The container view for the host form.
    """
    def __init__(self, page: Page, host: Host, host_tile: Container, list_of_hosts: Column, host_form_view: Container):
        self.page = page
        self.host = host
        self.host_tile = host_tile
        self.list_of_hosts = list_of_hosts
        self.host_form_view = host_form_view

        # Form Fields for Host Registration
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
        # On initialization, change on click to remove the host
        self.host_tile.content.controls[1].on_click = self.remove_self

    def remove_self(self, e) -> None:
        """
        Removes the host from the global host list and updates the UI.
        """
        index = find_dict_index(global_hosts, self.host.host_id)
        if index is not None:
            global_hosts.pop(index)
            writting_to_hosts()
        else:
            print("The host you are trying to remove hasn't been properly registered yet.")
        remove_from_selection(self.list_of_hosts, self.host.id_key)
        self.host_form_view.content.controls[2] = Column(expand=3)
        self.page.update()
        update_global_ui()

    def save_host_config(self, e):
        """
        Saves the host configuration and updates the global host list.
        """
        self.host.ssh_sudo_user = self.ssh_sudo_user_field.value
        self.host.identity_file = self.identity_file_field.value
        self.host.ssh_ip_address = self.ssh_ip_address_field.value
        self.host.ssh_port = self.ssh_port_field.value

        old_name = self.host.host_id
        index = find_dict_index(global_hosts, old_name)
        self.host.host_id = self.host_id_field.value

        if index is not None:
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
        print(global_hosts)  # Debug print
        self.host_tile.content.controls[0].value = self.host.host_id
        self.page.update()
        writting_to_hosts()
        update_global_ui()

    def validate_submit(self, e) -> None:
        """
        Validates the host form fields and enables/disables the submit button accordingly.
        """
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
        """
        Builds the host form for display.
        """
        return self._form


class HostTab:
    """
    A class to manage the Host Tab interface.

    Attributes:
        page (Page): The Flet page where the components are rendered.
    """
    def __init__(self, page: Page) -> None:
        self.page = page
        self.placeholder = Column(
            expand=3
        )
        self.list_of_hosts = Column(
            scroll=ScrollMode.ADAPTIVE,
            expand=2,
            controls=[
                OutlinedButton(text="Create a new host", on_click=self.add_new_host)
            ]
        )
        self.host_tab_view = Container(
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
        """
        Adds a new host and its corresponding form for setup.
        """
        new_host = Host(
            host_id="New Host",
            ssh_sudo_user="",
            identity_file="",
            ssh_ip_address="",
            ssh_port="",
        )
        host_tile = new_host.build_host_tile()
        host_form = HostForm(
            self.page,
            new_host,
            host_tile,
            self.list_of_hosts,
            self.host_tab_view
        )
        host_tile.on_click = lambda e: self.host_is_selected(e, host_form, host_tile)
        self.list_of_hosts.controls.append(host_tile)
        self.list_of_hosts.update()

    def host_is_selected(self, e, host_form: HostForm, host_tile: Container) -> None:
        """
        Displays the form for the selected host.

        Args:
            e: The event object.
            host_form (HostForm): The form template for the selected host.
            host_tile (Container): The container for the selected host tile.
        """
        self.host_tab_view.content.controls[2] = host_form.build_host_form()
        self.page.update()

    def build_hosts_tab(self) -> Container:
        """
        Builds the main container for the Host Tab.
        """
        return self.host_tab_view

# Helper function to write the host data to a file
def writting_to_hosts() -> None:
    write_to_hosts(global_hosts)

@staticmethod
def update_global_ui():
    global_event_bus.publish("update_global_ui", None)
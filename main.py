from nicegui import app, ui

@ui.page("/")
async def index():
    with ui.row():
        # Checkboxes
        with ui.column().style("float: left"):
            ui.label("Click what services you would like installed below")
            with ui.row():
                service1 = ui.checkbox('Actuator Agent')
                service2 = ui.checkbox('BACnet Proxy')
            with ui.row():
                service3 = ui.checkbox('Data Mover')
                service4 = ui.checkbox('DNP3 Agent')
            with ui.row():
                service5 = ui.checkbox('Forward Historian')
                service6 = ui.checkbox('IEEE 2030.5 Agent')
            with ui.row():
                service7 = ui.checkbox('MongoDB Tagging')
                service8 = ui.checkbox('MQTT Historian')
            with ui.row():
                service9 = ui.checkbox('OpenADR VEN Agent')
                service10 = ui.checkbox('Platform Driver Agent')
            with ui.row():
                service11 = ui.checkbox('SQL Aggregate Historian')
                service12 = ui.checkbox('SQL Historian')
            with ui.row():
                service13 = ui.checkbox('SQLite Tagging')
                service14 = ui.checkbox('VOLTTRON Central')
            with ui.row():
                service15 = ui.checkbox('VOLTTRON Central Platform')
                service16 = ui.checkbox('Weather Dot Gov')
            pick_services = ui.button("Pick Services")

        await pick_services.clicked()
        with ui.column():
            ui.label("Here are the services you have picked:")

            # List of Selected services that will show when appropriate services are picked
            ui.label('Actuator Agent').bind_visibility_from(service1, 'value')
            ui.label('BACnet Proxy').bind_visibility_from(service2, 'value')
            ui.label('Data Mover').bind_visibility_from(service3, 'value')
            ui.label('DNP3 Agent').bind_visibility_from(service4, 'value')
            ui.label('Forward Historian').bind_visibility_from(service5, 'value')
            ui.label('IEEE 2030.5 Agent').bind_visibility_from(service6, 'value')
            ui.label('MongoDB Tagging').bind_visibility_from(service7, 'value')
            ui.label('MQTT Historian').bind_visibility_from(service8, 'value')
            ui.label('OpenADR VEN Agent').bind_visibility_from(service9, 'value')
            ui.label('Platform Driver Agent').bind_visibility_from(service10, 'value')
            ui.label('SQL Aggregate Historian').bind_visibility_from(service11, 'value')
            ui.label('SQL Historian').bind_visibility_from(service12, 'value')
            ui.label('SQLite Tagging').bind_visibility_from(service13, 'value')
            ui.label('VOLTTRON Central').bind_visibility_from(service14, 'value')
            ui.label('VOLTTRON Central Platform').bind_visibility_from(service15, 'value')
            ui.label('Weather Dot Gov').bind_visibility_from(service16, 'value')
            ui.label("Click 'Confirm Services' to confirm your choices.")
            confirm_services = ui.button("Confirm Services")

    async def parseData():
        if getattr(service1, "value") == True:
            print(getattr(service1, "text"))

    await confirm_services.clicked()
    ui.label("Enter your password then click 'Install Services'")
    with ui.row():
        ui.input(label="Password", placeholder="Enter Password", password=True, password_toggle_button=True)
        ui.button("Install Services", on_click=parseData)

ui.run()



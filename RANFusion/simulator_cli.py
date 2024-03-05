#################################################################################################################################
# simulator_cli.py is located in root directory to allows you to type commands like ue-list to see the list of current UEs.     #
# execute various commands to manage and monitor the network's state, including listing gNodeBs, cells, sectors, UEs, and       #
# their respective logs and KPIs. It also supports commands for starting and stopping UE traffic, adding or deleting UEs, and   #
# manually triggering load balancing.                                                                                           #
#################################################################################################################################
import cmd
from colorama import init, Fore, Style as ColoramaStyle
init(autoreset=True)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
import time
from prettytable import PrettyTable
from threading import Event
import os
import threading
from network.ue import UE

# Assuming these are your custom modules for managing various aspects of the network simulator
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from network.NetworkLoadManager import NetworkLoadManager
from traffic.traffic_generator import TrafficController
from network.ue import UE
from network.sector import global_ue_ids

cli_style = Style.from_dict({
    'prompt': 'fg:green bold',  # Use 'green' instead of 'ansi.green'
})


# Define your aliases and commands in a more flexible structure
# For the purpose of this example, it's defined within the code, but it could be external
alias_config = {
    'aliases': [
        {'alias': 'gnb', 'command': 'gnb_list'},
        {'alias': 'cell', 'command': 'cell_list'},
        {'alias': 'sector', 'command': 'sector_list'},
        {'alias': 'ue', 'command': 'ue_list'},
        {'alias': 'ulog', 'command': 'ue_log'},
        {'alias': 'ukpi', 'command': 'ue_kpis'},
        # Add more aliases as needed
    ]
}

class SimulatorCLI(cmd.Cmd):
    
    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, network_load_manager, base_dir):
        super(SimulatorCLI, self).__init__()  # Correctly call the superclass initializer
        self.session = PromptSession()
        self.traffic_controller = TrafficController()
        self.base_dir = base_dir
        self.display_thread = None
        self.running = False
        # Assuming alias_config is defined
        self.aliases = self.generate_alias_mappings(alias_config)
        self.gNodeB_manager = gNodeB_manager
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.ue_manager = ue_manager  # If UEManager.get_instance() is necessary, make sure it's called correctly
        self.network_load_manager = network_load_manager
        self.stop_event = Event()
        self.in_kpis_mode = False

        # Setup for prompt_toolkit completion
        commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
        self.completer = WordCompleter(commands + list(self.aliases.keys()), ignore_case=True)

    # cmdloop to use prompt_toolkit
    def cmdloop(self, intro=None):
        self.print_global_help()  # Display custom help menu at startup
        stop = None
        while not stop:
            try:
                line = self.session.prompt(self.prompt, style=cli_style, completer=self.completer)
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            except (KeyboardInterrupt, EOFError):
                print("Exiting.")
                break
            
    @staticmethod
    def generate_alias_mappings(config):
        """Generates a dictionary mapping aliases to commands."""
        mappings = {}
        for item in config['aliases']:
            mappings[item['alias']] = item['command']
        return mappings

    intro = "Welcome to the RAN Fusion Simulator CLI.\nType --help to list commands.\n"
    prompt ='Cli-host ' 

    def precmd(self, line):
        line = line.strip()
        if line == 'exit':
            return 'exit'  # Ensures that 'exit' command is recognized and processed
        if line in self.aliases:
            return self.aliases.get(line, line)
        else:
            return line
        
    def do_help(self, arg):
        if arg in ['--help', '-h', '']:
            super().do_help(None)
        else:
            super().do_help(arg)
################################################################################################################################ 
    def do_ue_list(self, arg):
        args = arg.split()
        page = 1
        page_size = 10  # Default number of items per page
        if len(args) == 2:
            try:
                page = int(args[0])
                page_size = int(args[1])
            except ValueError:
                print("Invalid page or page_size. Using defaults.")

        def display_page(page, page_size):
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            # Fetch all UE IDs using UEManager
            ue_ids = self.ue_manager.list_all_ues()
            total_ues = len(ue_ids)
            ues_to_display = ue_ids[start_index:end_index]

            table = PrettyTable()
            table.field_names = ["UE ID", "Service Type", "Throughput(MB)"]
            table.align = "l"
            table.border = True
            table.header = True
            table.header_style = "title"

            for ue_id in ues_to_display:
                ue = self.ue_manager.get_ue_by_id(ue_id)
                if ue:
                    throughput_mbps = ue.throughput / 1e6  # Convert throughput to Mbps
                    table.add_row([ue.ID, ue.ServiceType, f"{throughput_mbps:.2f}"])

            print(table)
            total_pages = total_ues // page_size + (1 if total_ues % page_size > 0 else 0)
            print(f"Page {page} of {total_pages}")

        def refresh_data():
            while not self.stop_event.is_set():
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
                display_page(page, page_size)  # Display the current page
                time.sleep(1)  # Wait for a second before refreshing

            self.stop_event = threading.Event()
            display_thread = threading.Thread(target=refresh_data)
            display_thread.start()

            input("Press Enter to stop refreshing...")  # Wait for user input to stop refreshing
            self.stop_event.set()
            display_thread.join()

        # Handling pagination manually after stopping the refresh
        while True:
            next_action = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").lower()
            if next_action == 'n':
                page += 1
            elif next_action == 'p' and page > 1:
                page -= 1
            elif next_action == 'q':
                break
            else:
                print("Invalid input. Please try again.")

            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
            display_page(page, page_size)  # Display the updated page

############################################################################################################################## 
    def do_ue_log(self, arg):
        """Display UE (User Equipment) traffic logs."""
        print("Displaying UE traffic logs. Press Ctrl+C to return to the CLI.")
        try:
            # Initialize PrettyTable with column headers based on your log structure
            table = PrettyTable(["UE ID", "Service Type", "Throughput (MB)", "Interval (s)", "Delay (ms)", "Jitter (%)", "Packet Loss Rate (%)"])
            with open('traffic_logs.txt', 'r') as log_file:
                for line in log_file:
                    # Assuming each log entry is a comma-separated value line
                    # You'll need to adjust parsing based on your actual log format
                    parts = line.split(',')  # This is an example; adjust based on your actual log format
                    if len(parts) < 7:
                        continue  # Skip malformed lines
                    # Add a row to the table for each log entry
                    # Adjust index and parsing as necessary based on the actual log format
                    table.add_row(parts)
            print(table)
        except FileNotFoundError:
            print("Log file not found. Ensure traffic logging is enabled.")
        except KeyboardInterrupt:
            print("\nReturning to CLI...")
################################################################################################################################ 
    def do_gnb_list(self, arg):
        """List all gNodeBs with details."""
        gNodeB_details_list = self.gNodeB_manager.list_all_gNodeBs_detailed()
        gNodeB_loads = self.network_load_manager.calculate_gNodeB_load()
        if not gNodeB_details_list:
            print("No gNodeBs found.")
            return

        # Create a PrettyTable instance
        table = PrettyTable()

        # Define the table columns
        table.field_names = ["gNodeB ID", "Latitude", "Longitude", "Coverage Radius", "Transmission Power", "Bandwidth", "Load %"]

        # Adding rows to the table
        for gNodeB in gNodeB_details_list:
            gNodeB_id = gNodeB['id']
            load_percentage = gNodeB_loads.get(gNodeB_id, 0)
            coverage_radius = gNodeB.get('coverage_radius', 'N/A')
            transmission_power = gNodeB.get('transmission_power', 'N/A')
            bandwidth = gNodeB.get('bandwidth', 'N/A')
            load_percentage = gNodeB_loads.get(gNodeB['id'], 0)
            table.add_row([
                gNodeB['id'], 
                gNodeB['latitude'], 
                gNodeB['longitude'], 
                coverage_radius, 
                transmission_power, 
                bandwidth,
                f"{load_percentage:.2f}%" 
            ])
    
        # Optional: Set alignment for each column if needed
        table.align = "l"  # Left align the text
    
        # Print the table
        print(table) 
################################################################################################################################ 
    def do_cell_list(self, arg):
        """List all cells with their load percentage."""
        def display_cell_list():
            while not self.stop_event.is_set():
                cell_details_list = self.cell_manager.list_all_cells_detailed()
                if not cell_details_list:
                    print("No cells found.")
                    break  # Exit the loop if no cells are found

                table = PrettyTable()
                table.field_names = ["Cell ID", "Technology", "Status", "Active UEs", "Cell Load (%)"]

                for cell_detail in cell_details_list:
                    cell_id = cell_detail['id']
                    cell = self.cell_manager.get_cell(cell_id)  # Retrieve the cell object by its ID
                    if cell is None:
                        continue  # Skip if the cell is not found

                    technology = cell_detail.get('technology', '5GNR')
                    status_text = "\033[92mActive\033[0m" if cell_detail.get('Active', True) else "\033[91mInactive\033[0m"
                    active_ues = self.calculate_active_ues_for_cell(cell_id)  # Calculate active UEs for each cell

                    # Calculate the load of the cell using the NetworkLoadManager
                    cell_load_percentage = self.network_load_manager.calculate_cell_load(cell)
            
                    table.add_row([
                        cell_id,
                        technology,
                        status_text,
                        active_ues,
                        f"{cell_load_percentage:.2f}%"  # Format the cell load as a percentage
                    ])

                os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console for each update
                print(table)
                time.sleep(1)  # Refresh the table every second

        self.stop_event = threading.Event()
        display_thread = threading.Thread(target=display_cell_list)
        display_thread.start()

        input("Press Enter to stop displaying cell load...")  # Wait for user input to stop the dynamic display
        self.stop_event.set()
        display_thread.join()

    def calculate_active_ues_for_cell(self, cell_id):
        # Retrieve the cell object by its ID using the correct method name
        cell = self.cell_manager.get_cell(cell_id)
        if cell is None:
            return 0  # Return 0 if the cell is not found
        # Return the count of active UEs for the cell
        return len(cell.ConnectedUEs)
################################################################################################################################ 
    def do_sector_list(self, arg):
        """List all sectors"""
        sector_list = self.sector_manager.list_all_sectors()
        if not sector_list:
            print("No sectors found.")
            return
        # Create a PrettyTable instance
        table = PrettyTable()
        # Define the table columns including Current Load (%)
        table.field_names = ["Sector ID", "Cell ID", "Max UEs", "Active UEs", "Max Throughput", "Sector Load (%)"]
        # Adding rows to the table
        for sector_info in sector_list:
            sector_id = sector_info['sector_id']
            # Retrieve the Sector object using the sector_id
            sector = self.sector_manager.get_sector_by_id(sector_id)  # Assuming there's a method like this in SectorManager
            if sector is None:
                continue  # Skip if the sector is not found

            sector_load_percentage = self.network_load_manager.calculate_sector_load(sector)
        
            table.add_row([
                sector_info['sector_id'],
                sector_info['cell_id'],
                sector_info['capacity'],
                sector_info['current_load'],
                sector_info['max_throughput'],
                f"{sector_load_percentage:.2f}%"  # Display the calculated load percentage
            ])
        # Optional: Set alignment for each column
        table.align["Sector ID"] = "l"
        table.align["Cell ID"] = "l"
        table.align["Max UEs"] = "r"
        table.align["Active UEs"] = "r"
        table.align["Max Throughput"] = "r"
        table.align["Sector Load (%)"] = "r"  # Align the new column to the right
        # Print the table
        print(table)
################################################################################################################################            
    def do_del_ue(self, line):
        from network.sector import global_ue_ids

        ue_id = line.strip().lower()  # Convert UE ID to lowercase for case-insensitive processing
        if not ue_id:
            print("Usage: del_ue <ue_id>")
            return

        print(f"Trying to delete UE {ue_id}")

        # Use UEManager to get the UE instance in a case-insensitive manner
        ue_manager = UEManager.get_instance(self.base_dir)

        # Use UEManager's delete_ue method to encapsulate the deletion logic
        try:
            if ue_manager.delete_ue(ue_id):
                print(f"UE {ue_id} has been successfully removed.")
            else:
                print(f"Failed to remove UE {ue_id}.")
        except Exception as e:
            print(f"Error removing UE: {e}")
################################################################################################################################
    def handle_command(command):
        # Assuming the command format is "add_ue ue <UE_ID>,<Sector_ID>,<Service_Type>"
            _, ue_id, sector_id, service_type = command.split()
            add_ue(ue_id, sector_id, service_type)

    def add_ue(ue_id, sector_id, service_type):
        # You would call a method here to handle the addition of the UE.
        # This method would need to be defined in a suitable class, such as UeManager.
        # It would involve creating a new UE instance with the specified parameters
        # and adding it to the specified sector.
        ue_config = {
            "ue_id": ue_id,
            "connected_sector": sector_id,
            "service_type": service_type
        }
        # Assuming UEManager is already instantiated and accessible
        ue_manager.create_ue(ue_config)
################################################################################################################################ 
    def do_kpis(self, arg):
        """
        Enter the KPIs submenu.
        """
        self.in_kpis_mode = not self.in_kpis_mode # Toggle KPIs mode
        if self.in_kpis_mode:
            init(autoreset=True)
            self.prompt = 'Cli-host ' 
        else:
            self.prompt = f'{Fore.GREEN}Cli-host{Style.RESET_ALL} '
        print("Entered KPIs submenu...")
################################################################################################################################
    def do_loadbalancing(self, arg):
        """
        call loadbalancing manually triggered by typing 'loadbalancing' in the CLI.the optimze the load of the each cell/sector
        """
        # Implement the logic call display load balancing information here.
        print("Displaying load balancing massagage...")

################################################################################################################################ 
    def print_global_help(self):
        if not self.in_kpis_mode:
            print(f"\n{Fore.GREEN}Global options:{ColoramaStyle.RESET_ALL}")
            print(f"  {Fore.GREEN}--help{Fore.RESET}        Show this help message and exit")
            print(f"\n{ColoramaStyle.BRIGHT}Available commands:{ColoramaStyle.RESET_ALL}")
            for command, description in [
                ('cell_list', 'List all cells in the network.'),
                ('gnb_list', 'List all gNodeBs in the network.'),
                ('sector_list', 'List all sectors in the network.'),
                ('ue_list', 'List all UEs (User Equipments) in the network.'),
                ('ue_log', 'Display UE traffic logs.'),
                ('del_ue', 'delete ue from sector and database'),
                ('add_ue', 'add new ue based on current config file to the specific sector'),
                ('kpis', 'Display KPIs for the network.'),
                ('loadbalancing', 'Display load balancing information for the network.'),
                ('start_ue', 'Start the ue traffic.'),
                ('stop_ue', 'Stop the ue traffic.'),
                ('exit', 'Exit the Simulator.')
            ]:
                print(f"  {Fore.CYAN}{command}{Fore.RESET} - {description}")
        else:
            # KPIs submenu help message
            print(f"\n{ColoramaStyle.BRIGHT}KPIs submenu commands:{ColoramaStyle.RESET_ALL}")
            for command, description in [
                ('ue_kpis', 'Display KPIs for User Equipments (UEs).'),
                ('exit', 'Return to the main menu.'),
            ]:
                print(f"  {Fore.CYAN}{command}{Fore.RESET} - {description}")
        print()

################################################################################################################################ 
    def do_stop_ue(self, arg):
        """Stop traffic generation for a specific UE."""
        if not arg:
            print("Please provide a UE ID.")
            return
        try:
            # Ensure the UE ID is in the correct format (e.g., "UE10")
            ue_id = f"UE{arg}"
            # Retrieve the UE object using the UE ID
            ue = UE.get_ue_instance_by_id(ue_id)
            if not ue:
                print(f"UE with ID {ue_id} not found.")
                return
            # Assuming there's a method in ue_manager to stop traffic for a UE
            self.traffic_controller.stop_ue_traffic(ue)
            print(f"Traffic generation for UE {ue.ID} has been stopped.")
        except Exception as e:
            print(f"Error stopping traffic for UE: {e}")

    def do_start_ue(self, arg):
        """Start traffic generation for a specific UE."""
        if not arg:
            print("Please provide a UE ID.")
            return
        try:
            # Ensure the UE ID is in the correct format (e.g., "UE10")
            ue_id = f"UE{arg}"
            # Retrieve the UE object using the UE ID
            ue = UE.get_ue_instance_by_id(ue_id)
            if not ue:
                print(f"UE with ID {ue_id} not found.")
                return
            # Call the start_ue_traffic method with the UE object
            self.traffic_controller.start_ue_traffic(ue)
            print(f"Traffic generation for UE {ue.ID} has been started.")
        except Exception as e:
            print(f"Error starting traffic for UE: {e}")
################################################################################################################################
    def complete(self, text, state):
        # Filter completions matching the text and return one by one
        results = [cmd for cmd in self.completions if cmd.startswith(text)] + [None]
        return results[state]

    def commands_with_aliases(self, text):
        # Include both commands and aliases that start with 'text'
        commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_') and cmd[3:].startswith(text)]
        aliased_commands = [alias for alias, cmd in self.aliases.items() if alias.startswith(text)]
        return commands + aliased_commands

    def complete_default(self, text, line, begidx, endidx):
        # Implement your default auto-completion logic here, if any...
        return []

    def complete_gnb_list(self, text, line, begidx, endidx):
        # Assuming self.gNodeB_manager.gnbs is a list of gNodeB names
        if hasattr(self.gNodeB_manager, 'gnbs'):
            return [gnb for gnb in self.gNodeB_manager.gnbs if gnb.startswith(text)]
        return []

    # For alias 'gnb', just delegate to complete_gnb_list
    def complete_gnb(self, *args):
        return self.complete_gnb_list(*args)
    
    def complete_ue_log(self, text, line, begidx, endidx):
        # Since ue_log might not have specific arguments to complete, return an empty list
        # Or, return common log-related suggestions if applicable
        return []
    
    def complete_ulog(self, *args):
        return self.complete_ue_log(*args)
    
    def default(self, line):
        if line.strip() in ['--help', '-h']:
            self.do_help('')
        else:
            print("*** Unknown syntax:", line)

    def do_exit(self, arg):
        """Exit the simulator."""
        print("Exiting the simulator...")
        return True
#############################################################################################################
    def precmd(self, line):
        line = line.strip()
    
        if self.in_kpis_mode:
            if line == "exit":
                # Exit KPIs submenu
                self.in_kpis_mode = False
                self.prompt = 'Cli-host '  
                return ''  # Return empty string to prevent further processing
            elif line not in ['ue_kpis']:
                print("Invalid command in KPIs submenu. Available commands: 'ue_kpis', 'exit'")
                return ''  # Return empty string to prevent further processing
    
        elif line in self.aliases:
            return self.aliases.get(line, line)
        
        return line
#############################################################################################################

#############################################################################################################
    def do_ue_kpis(self, arg):
        if not self.in_kpis_mode:
            print("UE KPIs command is only available in the KPIs submenu.") 
            return
    
        # Display KPIs
        print("Displaying UE KPIs...")
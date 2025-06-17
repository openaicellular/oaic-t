# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions using AI Fuzzing to generate testing signals
import sys
# adding Folder_2 to the system path
sys.path.insert(0, '../../RANFusion/')


from actor_logger import logger
from task import Action
from actions.action_executor import ActionExecutor
import time
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from traffic.traffic_generator import TrafficController
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from network.NetworkLoadManager import NetworkLoadManager
from network.network_delay import NetworkDelay
import numpy as np
import os
from aicore.gafuzzer import GAFuzzerRANSim
from threading import Thread


ue_manager = None


def generate_traffic_loop(traffic_controller, ue_list, network_load_manager, network_delay_calculator,
                          db_manager):
    print(f"Debug: inside generate_traffic_loop of main.py ")  # Debugging line
    while True:
        for ue in ue_list:
            throughput_data = traffic_controller.calculate_throughput(ue)
            # need to double check if ue.delay is updated or not in the following function
            network_load_manager.network_measurement()
        time.sleep(1)

# This action is to reset the simulator to the initial state
class ActionRadioSimulatorStart(ActionExecutor):
    ACTION_NAME = "Start RANFusion Simulator"  ## Be sure this action name is the one used in the test script



    def run(selfs):
        ## To Be Implement
        # Database connection
        global ue_manager
        if ue_manager is not None:
            action_output_summary = "Success! The RANFusion has been already running..."
            action_output = action_output_summary
            return action_output_summary, action_output

        db_manager = DatabaseManager.get_instance()
        if db_manager.test_connection():
            print("Connection to InfluxDB successful.")
        else:
            print("Failed to connect to InfluxDB. Exiting...")
            return

        # Network Initialization
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(base_dir)
        gNodeB_manager = gNodeBManager.get_instance(base_dir=base_dir)
        gNodeBs, cells, sectors, ues, cell_manager = initialize_network(base_dir, num_ues_to_launch=5)
        print("Network Initialization Complete")

        # Additional setup
        sector_manager = SectorManager.get_instance(db_manager=db_manager)
        network_load_manager = NetworkLoadManager.get_instance(cell_manager, sector_manager, gNodeB_manager)

        ue_manager = UEManager.get_instance(base_dir)
        network_delay_calculator = NetworkDelay()

        traffic_controller_instance = TrafficController()
        traffic_thread = Thread(target=generate_traffic_loop, args=(traffic_controller_instance, ues, network_load_manager, network_delay_calculator, db_manager,))
        traffic_thread.start()

        monitoring_thread = Thread(target=network_load_manager.monitoring)
        monitoring_thread.start()

        action_output_summary = "Success! The RANFusion is running..."
        action_output = "Success! The RANFusion is running..."
        return action_output_summary, action_output


# This action is to reset the simulator to the initial state
class ActionRadioSimulatorRst(ActionExecutor):
    ACTION_NAME = "Radio Simulator Reset"  ## Be sure this action name is the one used in the test script

    def run(selfs):
        ## To Be Implement
        action_output_summary = "Fail. The function is not implemented yet!"
        action_output = "N/A"
        return action_output_summary, action_output


# This action is to start UEs and generate traffic randomly
class ActionTrafficGenRandom(ActionExecutor):
    ACTION_NAME = "Generate Random Traffics"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        global ue_manager
        if ue_manager is None:
            action_output_summary = "Fail! Please start the RANFusion Simulator first."
            action_output = action_output_summary
            return action_output_summary, action_output

        white_noise_std = self.action.get_action_para('white_noise_std')
        white_noise_mean = self.action.get_action_para('white_noise_mean')
        num_actions = self.action.get_action_para('num_actions')
        result = "KPI of UEs ... \n"
        print(result)
        for i in range(num_actions):
            result = result + "  The " + str(i) + "th random traffic generation action ... \n"
            for ue in ue_manager.ues:
                new_traffic = np.random.normal(white_noise_mean, white_noise_std, 1)
                ue.throughput = ue.throughput + new_traffic
            time.sleep(1)
            tmp_results = ""
            for ue in ue_manager.ues:
                tmp = "    " + ue.ID + ": throughput_" + ue.throughput + " delay_" + ue.delay + "\n"
                tmp_results = tmp_results + tmp
            print(tmp_results)
            result = result + tmp_results

        action_output_summary = "Success! The Random Traffic Generation is done!"
        action_output = result
        return action_output_summary, action_output


# This action is to start UEs and generate traffic using AI Fuzzing method
class ActionTrafficGenAIF(ActionExecutor):
    ACTION_NAME = "AIF Traffic Generation"  ## Be sure this action name is the one used in the test script

    ## computer the fittness of a population based on delay
    def calc_fittness_delay(self, ues):
        fittness = 0
        for ue_id in ues:
            ue = ues[ue_id]
            if ue.ServiceType == "video":
                fittness = fittness + 0.2 * ue.ue_delay
            elif ue.ServiceType == "game":
                fittness = fittness + ue.ue_delay
            elif ue.ServiceType == "voice":
                fittness = fittness + ue.ue_delay
            elif ue.ServiceType == "data":
                fittness = fittness + 0.1 * ue.ue_delay
            elif ue.ServiceType == "IoT":
                fittness = fittness + 0.8 * ue.ue_delay
            else:
                print("Error in UE's Service Type. Unknown service type: " + ue.ServiceType)
        return fittness

    def run(self):
        result = "Action running: " + self.action.name + " ..."
        print(result)

        result = result + "\n"
        global ue_manager
        if ue_manager is None:
            action_output_summary = "Fail to run AIF Traffic Generation! Please start the RANFusion Simulator first."
            action_output = result + action_output_summary
            return action_output_summary, action_output

        aif_method = self.action.get_action_para('aif_method')
        ues = ue_manager.ues
        num_ues = len(ues)

        if aif_method == "GA":
            print("Running GA algorithm ...")
            num_max_gen = self.action.get_action_para('num_max_gen')
            num_pop = self.action.get_action_para('num_pop')
            print("Running GA Fuzzing ...")
            fuzzerRANSim = GAFuzzerRANSim(num_pop, num_ues)
            pops = fuzzerRANSim.populations

            # apply the traffic throughput to each UE and check the kpi
            fittness_all = []
            for i in range(num_pop):
                pop_ind = pops[i]
                j = 0
                for ue_id in ues:
                    ue = ues[ue_id]
                    ue.throughput = pop_ind[j]
                    j = j + 1

                time.sleep(1)
                fittness = self.calc_fittness_delay(ues)
                print(fittness_all)
                fittness_all.append((pop_ind, fittness))

            best = min(fittness_all, key=lambda item: item[1])
            best_individual = best[0]
            best_fitness = best[1]

            # save all best to identify a significant increase
            best_fitness_all = [best_fitness]

            # keep generating new pops and measures the fittness
            generation = 0
            while best_fitness >= 0 and generation < num_max_gen:
                print("generation: " + str(generation) + " best fitness: " + str(best_fitness))
                generation += 1

                # get new population based on mutation and crossover
                pops = fuzzerRANSim.next_paras(fittness_all)

                # apply the traffic throughput to each UE and check the kpi
                fittness_all = []
                for i in range(num_pop):
                    pop_ind = pops[i]
                    j = 0
                    for ue_id in ues:
                        ue = ues[ue_id]
                        ue.throughput = pop_ind[j]
                        j = j + 1

                    time.sleep(1)
                    fittness = self.calc_fittness_delay(ues)
                    print(fittness_all)
                    fittness_all.append((pop_ind, fittness))

                best = min(fittness_all, key=lambda item: item[1])
                best_individual = best[0]
                best_fitness = best[1]
                best_fitness_all.append(best_fitness)
                result = (result + "Best fitness at generation: " + str(generation) + ": " + str(best_individual) + " best fitness:" + str(best_fitness))

                print("Best fitness at generation: " + str(generation) + ": " + str(best_individual) + " best fitness:" + str(best_fitness))


                if len(best_fitness_all) >= 2:
                    avg_pre = np.mean(np.array(best_fitness_all[:-1]))
                    std_pre = np.std(np.array(best_fitness_all[:-1])) + 0.1
                    print("avg_pre: " + str(std_pre) + "  std_pre:" + str(std_pre))
                    print(best_fitness_all[-1])
                    if best_fitness_all[-1] - avg_pre >= std_pre:
                        print("A significant increase of fitness value is detected!")
                        result = result + "A significant increase of fitness value is detected!"
                        break

        elif aif_method == "Search":
            print("To Be Supported")
        else:
            print("Unknown AIF method!")

        action_output_summary = "Success! The AIF Traffic Generation is done!"
        action_output = result
        return action_output_summary, action_output

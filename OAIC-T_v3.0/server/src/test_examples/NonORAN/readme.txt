This folder contains test script examples which run srsran epc, enodeb, and ue with traffic generation without involving ORAN RIC, i.e., E2 interface. These test scripts are good practices for you to get familiar with the test script structure and available test actions.

More important notes: 
1. SRSRAN framework currently requires restarting gNodeB after a UE is detached. This is the reason why our test scripts always include a "Stop ENodeB" action if a "Start ENodeB" action has been executed just for the purpose of clearing up the test environment. 

2. iperf traffic generation requires the installation of iperf in your computer. Pleas run "sudo apt install iperf3" before the running of iperf3 traffic generation test script.

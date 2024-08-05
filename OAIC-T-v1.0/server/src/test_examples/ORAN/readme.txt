This folder contains test script examples which run srsran ue with traffic generation when srsran epc and gnodeb has already started up, following the "Setup your own 5G Network" in oaic document: https://openaicellular.github.io/oaic/setup5gnetwork.html 

These test scripts also include one test action "Connect Test xApp" which connects to our Test xApp to collect KPI metrics in the RIC. These metrics will be displayed in one pannel of GUI. To enable this feature, KPIMon xApp and Test xApp must be deployed in the RIC. 

More important notes: 
1. SRSRAN framework currently requires restarting gNodeB after a UE is detached. Since our test script examples includes a "Stop UE" action, you must restart the gNodeB whenever the test script is completed. 

2. iperf traffic generation requires the installation of iperf in your computer. Pleas run "sudo apt install iperf3" before the running of iperf3 traffic generation test script.

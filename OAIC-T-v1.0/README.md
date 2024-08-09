# About OAIC-T
OAIC-T is an open-source AI cellular testing platform which supports automated, distributed, and AI-enhanced testing of xApps in O-RAN. 

# Motivations of OAIC-T
While AI models are enablers to achieve intelligent next-G wireles networks, comprehensive testing of their performance is cumbersome and in many cases non-existent. This is mainly due to the inability of the current theory to explain or prevent failures in the AI models which are mainly trained in data-driven manners. Hence, it is necessary to have a framework and appropriate environment for testing AI models in their capacity of cellular RAN controllers. From the ongoing research and development and expected deployment of O-RAN components in Next-G networks, there is a urgent need for methods, platforms, and tools that facilitate testing various AI models in the radio network in a production like environment.

# Key Design Requirements of OAIC-T
1. Software-defined and modular to enable customization;
2. Invasive/non-invasive testing during O-RAN operation in isolated or production environment to capture data in relevant operating conditions;
3. Open test interfaces to enable the development of new test methods and processes;
4. Test configuration files that enable specifying and reproducing a test;
5. Support for automated and AI-enhanced testing to assess the operation of AI-enabled cellular radio network controllers under a myriad of channel and contextual conditions (large search spaces)
6. Support for multitasking and distributed testing to enable a multi-user testing environment (e.g., producing different traffic scenarios)

# OAIC-T Framework
An OAIC-T test involves automated setup of the testing environment, automated test execution, and automated generation of testing performance report. The OAIC-T framework consists of three major components: the OAIC-T server which sets up the testing environment as described in test configuration files and orchestrates the test execution as defined in test cases, the OAIC-T actor which executes test steps as instructed by the OAIC server, and the test repository which stores various test assets (e.g., test files, data files, log files, test results, etc.). 

<img src="/docs/source/oaci_t_framework.png" width=70% height=70%>


# Major Release Milestones of OAIC-T
1. Phase I (Expected Date: Jan. 1, 2023) with implementations of core OAIC-T framework.	
2. Phase II (Expected Date: June. 15, 2023) with implementations of AI testing methods, including Fuzzing, AI-Fuzzing, and adversarial learning.
3. Phase III (Expected Date: Dec. 15, 2023) with implementations of multitasking.
4. Phase IV (Expected Date: June. 15, 2024) with system integration and testing.


# How to Run OAIC-T
Please refer to the [OAIC-T document](https://openaicellular.github.io/oaic/oaic_t.html) for details.


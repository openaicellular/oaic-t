import re


if __name__ == '__main__':
    line = "Network attach successful. IP: '172.16.0.8'"
    if 'Network attach successful' in line:
        UE_Network_Attach = True
        ip_pattern = re.compile(r'[0-9]+(?:\.[0-9]+){3}')
        UE_IP = ip_pattern.findall(line)
        print(UE_IP[0])
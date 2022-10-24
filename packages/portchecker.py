import socket
from ipaddress import IPv4Address, IPv6Address, ip_address
import json

def is_ip_address(address: str) -> bool:
    try:
        return bool(ip_address(address))
    except ValueError:
        return False


def is_address_valid(address: str) -> bool:
    address_obj = ip_address(address)
    if address_obj.is_private:
        raise ValueError(
            f"IPv{address_obj.version} address '{address}' does not appear to be public"
        )
    return address_obj.version


def is_valid_hostname(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        raise Exception("Hostname does not appear to resolve")

def generate_return(result: dict, status: int) -> dict:
    return {
        "statusCode": status,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(result),
    }

def query_ipv4(address, ports):
    results = []
    for port in ports:
        result = {"port": port, "status": False}
        sock = socket.socket()
        sock.settimeout(2)
        port_check = sock.connect_ex((address, int(port)))
        if port_check == 0:
            result["status"] = True
        sock.close()
        results.append(result)
    return results

def main(args):
    ret = {"error": False, "host": None, "check": [], "msg": None}

    try:
        ret["host"] = args["host"]
    except Exception as ex:
        ret["error"] = True
        ret["msg"] = "A host must be defined"
        return generate_return(ret, 400)

    try:
        ports = args["ports"]
    except Exception as ex:
        ret["error"] = True
        ret["msg"] = "A list of ports must be defined"
        return generate_return(ret, 400)

    is_ip = is_ip_address(ret["host"])
    version = 4
    try:
        if is_ip:
            version = is_address_valid(ret["host"])
        else:
            is_valid_hostname(ret["host"])
    except Exception as ex:
        ret["error"] = True
        ret["msg"] = str(ex)
        return generate_return(ret, 400)

    if version == 6:
        ret["error"] = True
        ret["msg"] = "IPv6 is not currently supported"
        return generate_return(ret, 400)

    ret["check"] = query_ipv4(ret["host"], ports)
    return generate_return(ret, 200)
 

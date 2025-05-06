import selectors
import socket
from dnslib import DNSRecord, RR
from my_cache import Cache

DNS_PORT = 53
MAX_PACKET_SIZE = 512
cache = Cache()
selector = selectors.DefaultSelector()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", DNS_PORT))
    selector.register(server_socket, selectors.EVENT_READ, handle_request)

    print(f"Server is running on port {DNS_PORT}")
    try:
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
    finally:
        server_socket.close()

def handle_request(socket):
    data, addr = socket.recvfrom(MAX_PACKET_SIZE)
    request = DNSRecord.parse(data)
    domain_name = str(request.q.qname)
    question_type = request.q.qtype

    cache_key = f"{domain_name}_{question_type}"
    cached_answer = cache.get(cache_key)

    if cached_answer:
        reply = DNSRecord(header=request.header)
        reply.add_answer(*cached_answer)
        socket.sendto(reply.pack(), addr)
        return

    forwarder_addr = ('8.8.8.8', DNS_PORT)
    socket.sendto(data, forwarder_addr)

    response, _ = socket.recvfrom(MAX_PACKET_SIZE)
    response_packet = DNSRecord.parse(response)

    answers = list(response_packet.rr)
    cache.save_in_cache(answers, domain_name, question_type)

    socket.sendto(response, addr)

if __name__ == "__main__":
    main()
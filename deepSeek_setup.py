# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
import httpx
import hashlib
import ssl

# Expected SHA256 fingerprint of api.deepseek.com's certificate
DEEPSEEK_CERT_FINGERPRINT = "A5:B3:35:6B:06:1D:0D:3C:94:C8:EE:CE:A4:AF:BE:E5:C8:0B:46:7B:E0:C0:7E:18:0D:46:83:18:60:02:8C:49"

class CertPinningTransport(httpx.HTTPTransport):
    def __init__(self):
        super().__init__(verify=False)
        
    def _get_connection(self, request):
        connection = super()._get_connection(request)
        
        # Verify certificate fingerprint after connection
        if request.url.host == "api.deepseek.com":
            sock = connection.sock
            if hasattr(sock, 'getpeercert'):
                cert = sock.getpeercert(binary_form=True)
                cert_hash = hashlib.sha256(cert).hexdigest().upper()
                expected_hash = DEEPSEEK_CERT_FINGERPRINT.replace(":", "")
                if cert_hash != expected_hash:
                    raise ssl.SSLError(f"Certificate fingerprint mismatch: {cert_hash}")
                    
        return connection

client = OpenAI(
    api_key="sk-002db16d9bef4d91ad8b214abc7cc916", 
    base_url="https://api.deepseek.com/v1",
    http_client=httpx.Client(transport=CertPinningTransport())
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Tell me about prompt enginner"},
    ],
    stream=False
)

print(response.choices[0].message.content)

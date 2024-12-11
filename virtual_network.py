CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=ClientNetworkAdapter"
PAYLOAD = '''
<ClientNetworkAdapter:ClientNetworkAdapter xmlns:ClientNetworkAdapter="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
    <Metadata>
        <Atom>
        </Atom>
    </Metadata>
    <PortVLANID kb="CUR" kxe="false">2133</PortVLANID>
    <VirtualSwitchID kxe="false" kb="ROR">0</VirtualSwitchID>
    <VirtualSwitchName ksv="V1_12_0" kb="ROR" kxe="false">ETHERNET0</VirtualSwitchName>
</ClientNetworkAdapter:ClientNetworkAdapter>
'''
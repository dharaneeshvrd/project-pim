import string_util as util

CONTENT_TYPE = "application/vnd.ibm.powervm.uom+xml; Type=VirtualIOServer"

def populate_payload(hmc_host, partition_uuid, system_uuid, physical_volume_name):
    return f'''
    <VirtualIOServer:VirtualIOServer xmlns:VirtualIOServer="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/" xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
    <Metadata>
        <Atom>
        </Atom>
    </Metadata>
    <AllowPerformanceDataCollection kb="CUD" kxe="false">false</AllowPerformanceDataCollection>
    <AssociatedPartitionProfile kxe="false" kb="CUD" href="https://9.47.88.249:443/rest/api/uom/VirtualIOServer/5F2BF488-D5E5-43AC-BAB2-7D20C22C26C8/LogicalPartitionProfile/1ee06cd2-2fc8-3dee-ae85-acae7542cb7e" rel="related"/>
    <AvailabilityPriority kxe="false" kb="UOD">191</AvailabilityPriority>
    <CurrentProcessorCompatibilityMode kb="ROO" kxe="false">POWER9_Base</CurrentProcessorCompatibilityMode>
    <CurrentProfileSync kxe="false" kb="CUD">On</CurrentProfileSync>
    <IsBootable ksv="V1_3_0" kxe="false" kb="ROO">true</IsBootable>
    <IsConnectionMonitoringEnabled kxe="false" kb="UOD">true</IsConnectionMonitoringEnabled>
    <IsOperationInProgress kb="ROR" kxe="false">false</IsOperationInProgress>
    <IsRedundantErrorPathReportingEnabled kxe="false" kb="UOD">false</IsRedundantErrorPathReportingEnabled>
    <IsTimeReferencePartition kb="UOD" kxe="false">true</IsTimeReferencePartition>
    <IsVirtualServiceAttentionLEDOn kxe="false" kb="ROR">false</IsVirtualServiceAttentionLEDOn>
    <IsVirtualTrustedPlatformModuleEnabled kb="UOD" kxe="false">false</IsVirtualTrustedPlatformModuleEnabled>
    <KeylockPosition kb="CUD" kxe="false">normal</KeylockPosition>
    <LogicalSerialNumber kb="ROR" kxe="false">138C5AA1</LogicalSerialNumber>
    <OperatingSystemVersion kxe="false" kb="ROR">VIOS 3.1.4.10 </OperatingSystemVersion>
    <PartitionID kxe="false" kb="COD">1</PartitionID>
    <PartitionIOConfiguration kxe="false" kb="CUD" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <MaximumVirtualIOSlots kb="CUD" kxe="false">400</MaximumVirtualIOSlots>
        <ProfileIOSlots kb="CUD" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">1 Gigabit Ethernet (UTP) 4 Port Adapter PCIE-4x/Short</Description>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PartitionID ksv="V1_3_0" kb="ROO" kxe="false">1</PartitionID>
                    <PartitionName ksv="V1_3_0" kb="ROO" kxe="false">VIOS17-C340F2U03-ZZ</PartitionName>
                    <PartitionType ksv="V1_3_0" kb="ROO" kxe="false">Virtual IO Server</PartitionType>
                    <PCAdapterID kxe="false" kb="ROO">5719</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">512</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">5719</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">1056</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">5348</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">1</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">5348</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <IOAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553779219</AdapterID>
                            <Description kb="CUD" kxe="false">1 Gigabit Ethernet (UTP) 4 Port Adapter PCIE-4x/Short</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C11</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C11</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">C11</PhysicalLocation>
                            <UniqueDeviceID kb="ROR" kxe="false">5719</UniqueDeviceID>
                            <LogicalPartitionAssignmentCapable ksv="V1_2_0" kb="ROO" kxe="false">true</LogicalPartitionAssignmentCapable>
                            <DynamicPartitionAssignmentCapable ksv="V1_3_0" kb="ROR" kxe="false">true</DynamicPartitionAssignmentCapable>
                        </IOAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553779219</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C11</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">C11</SlotPhysicalLocationCode>
                    <SRIOVCapableDevice ksv="V1_3_0" kxe="false" kb="ROO">false</SRIOVCapableDevice>
                    <SRIOVCapableSlot ksv="V1_3_0" kxe="false" kb="ROO">true</SRIOVCapableSlot>
                    <SRIOVLogicalPortsLimit ksv="V1_3_0" kb="ROO" kxe="false">80</SRIOVLogicalPortsLimit>
                </AssociatedIOSlot>
            </ProfileIOSlot>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">PCIe3 x8 SAS RAID Internal Adapter 6Gb</Description>
                    <FeatureCodes kb="ROO" kxe="false">57D7</FeatureCodes>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PartitionID ksv="V1_3_0" kb="ROO" kxe="false">1</PartitionID>
                    <PartitionName ksv="V1_3_0" kb="ROO" kxe="false">VIOS17-C340F2U03-ZZ</PartitionName>
                    <PartitionType ksv="V1_3_0" kb="ROO" kxe="false">Virtual IO Server</PartitionType>
                    <PCAdapterID kxe="false" kb="ROO">842</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">260</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">842</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">1023</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">4116</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">2</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">4116</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <IOAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553910293</AdapterID>
                            <Description kb="CUD" kxe="false">PCIe3 x8 SAS RAID Internal Adapter 6Gb</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C49</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C49</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">C49</PhysicalLocation>
                            <UniqueDeviceID kb="ROR" kxe="false">842</UniqueDeviceID>
                            <LogicalPartitionAssignmentCapable ksv="V1_2_0" kb="ROO" kxe="false">true</LogicalPartitionAssignmentCapable>
                            <DynamicPartitionAssignmentCapable ksv="V1_3_0" kb="ROR" kxe="false">true</DynamicPartitionAssignmentCapable>
                        </IOAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553910293</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C49</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">C49</SlotPhysicalLocationCode>
                    <SRIOVCapableDevice ksv="V1_3_0" kxe="false" kb="ROO">false</SRIOVCapableDevice>
                    <SRIOVCapableSlot ksv="V1_3_0" kxe="false" kb="ROO">true</SRIOVCapableSlot>
                    <SRIOVLogicalPortsLimit ksv="V1_3_0" kb="ROO" kxe="false">80</SRIOVLogicalPortsLimit>
                </AssociatedIOSlot>
            </ProfileIOSlot>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">Universal Serial Bus UHC Spec</Description>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PartitionID ksv="V1_3_0" kb="ROO" kxe="false">1</PartitionID>
                    <PartitionName ksv="V1_3_0" kb="ROO" kxe="false">VIOS17-C340F2U03-ZZ</PartitionName>
                    <PartitionType ksv="V1_3_0" kb="ROO" kxe="false">Virtual IO Server</PartitionType>
                    <PCAdapterID kxe="false" kb="ROO">33345</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">3075</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">33345</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">1202</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">4172</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">2</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">4172</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <IOAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553713687</AdapterID>
                            <Description kb="CUD" kxe="false">Universal Serial Bus UHC Spec</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-T4</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-T4</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">T4</PhysicalLocation>
                            <UniqueDeviceID kb="ROR" kxe="false">33345</UniqueDeviceID>
                            <LogicalPartitionAssignmentCapable ksv="V1_2_0" kb="ROO" kxe="false">true</LogicalPartitionAssignmentCapable>
                            <DynamicPartitionAssignmentCapable ksv="V1_3_0" kb="ROR" kxe="false">true</DynamicPartitionAssignmentCapable>
                        </IOAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553713687</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-T4</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">T4</SlotPhysicalLocationCode>
                    <SRIOVCapableDevice ksv="V1_3_0" kxe="false" kb="ROO">false</SRIOVCapableDevice>
                    <SRIOVCapableSlot ksv="V1_3_0" kxe="false" kb="ROO">false</SRIOVCapableSlot>
                    <SRIOVLogicalPortsLimit ksv="V1_3_0" kb="ROO" kxe="false">0</SRIOVLogicalPortsLimit>
                </AssociatedIOSlot>
            </ProfileIOSlot>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">1 Gigabit Ethernet (UTP) 4 Port Adapter PCIE-4x/Short</Description>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5899</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5260</FeatureCodes>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PartitionID ksv="V1_3_0" kb="ROO" kxe="false">1</PartitionID>
                    <PartitionName ksv="V1_3_0" kb="ROO" kxe="false">VIOS17-C340F2U03-ZZ</PartitionName>
                    <PartitionType ksv="V1_3_0" kb="ROO" kxe="false">Virtual IO Server</PartitionType>
                    <PCAdapterID kxe="false" kb="ROO">5719</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">512</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">5719</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">1056</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">5348</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">1</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">5348</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <IOAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553713688</AdapterID>
                            <Description kb="CUD" kxe="false">1 Gigabit Ethernet (UTP) 4 Port Adapter PCIE-4x/Short</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C8</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C8</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">C8</PhysicalLocation>
                            <UniqueDeviceID kb="ROR" kxe="false">5719</UniqueDeviceID>
                            <LogicalPartitionAssignmentCapable ksv="V1_2_0" kb="ROO" kxe="false">true</LogicalPartitionAssignmentCapable>
                            <DynamicPartitionAssignmentCapable ksv="V1_3_0" kb="ROR" kxe="false">true</DynamicPartitionAssignmentCapable>
                        </IOAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553713688</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C8</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">C8</SlotPhysicalLocationCode>
                    <SRIOVCapableDevice ksv="V1_3_0" kxe="false" kb="ROO">false</SRIOVCapableDevice>
                    <SRIOVCapableSlot ksv="V1_3_0" kxe="false" kb="ROO">true</SRIOVCapableSlot>
                    <SRIOVLogicalPortsLimit ksv="V1_3_0" kb="ROO" kxe="false">510</SRIOVLogicalPortsLimit>
                </AssociatedIOSlot>
            </ProfileIOSlot>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">8 Gigabit PCI Express Dual Port Fibre Channel Adapter</Description>
                    <FeatureCodes kb="ROO" kxe="false">577D</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL58</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5273</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL2N</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5735</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL58</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5273</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL2N</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5735</FeatureCodes>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PCAdapterID kxe="false" kb="ROO">61696</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">3076</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">61696</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">906</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">4319</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">3</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">4319</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <PhysicalFibreChannelAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553713697</AdapterID>
                            <Description kb="CUD" kxe="false">8 Gigabit PCI Express Dual Port Fibre Channel Adapter</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C2</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C2</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">C2</PhysicalLocation>
                            <PhysicalFibreChannelPorts kb="CUD" kxe="false" schemaVersion="V1_0">
                                <Metadata>
                                    <Atom/>
                                </Metadata>
                                <PhysicalFibreChannelPort schemaVersion="V1_0">
                                    <Metadata>
                                        <Atom/>
                                    </Metadata>
                                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C2-T2</LocationCode>
                                    <PhysicalVolumes group="ViosStorage" kb="CUD" kxe="true" schemaVersion="V1_0">
                                        <Metadata>
                                            <Atom/>
                                        </Metadata>
                                    </PhysicalVolumes>
                                    <PortName kxe="false" kb="CUR">fcs1</PortName>
                                    <UniqueDeviceID kxe="false" kb="ROR">1aU78D3.001.WZS069F-P1-C2-T2</UniqueDeviceID>
                                    <WWPN kxe="false" kb="CUR">10000090fa1b6497</WWPN>
                                    <WWNN ksv="V1_3_0" kb="ROO" kxe="false">20000120fa1b6497</WWNN>
                                    <AvailablePorts kb="ROR" kxe="true">64</AvailablePorts>
                                    <TotalPorts kxe="true" kb="ROR">64</TotalPorts>
                                </PhysicalFibreChannelPort>
                                <PhysicalFibreChannelPort schemaVersion="V1_0">
                                    <Metadata>
                                        <Atom/>
                                    </Metadata>
                                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C2-T1</LocationCode>
                                    <PhysicalVolumes group="ViosStorage" kb="CUD" kxe="true" schemaVersion="V1_0">
                                        <Metadata>
                                            <Atom/>
                                        </Metadata>
                                    </PhysicalVolumes>
                                    <PortName kxe="false" kb="CUR">fcs0</PortName>
                                    <UniqueDeviceID kxe="false" kb="ROR">1aU78D3.001.WZS069F-P1-C2-T1</UniqueDeviceID>
                                    <WWPN kxe="false" kb="CUR">10000090fa1b6496</WWPN>
                                    <WWNN ksv="V1_3_0" kb="ROO" kxe="false">20000120fa1b6496</WWNN>
                                    <AvailablePorts kb="ROR" kxe="true">64</AvailablePorts>
                                    <TotalPorts kxe="true" kb="ROR">64</TotalPorts>
                                </PhysicalFibreChannelPort>
                            </PhysicalFibreChannelPorts>
                        </PhysicalFibreChannelAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553713697</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C2</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">C2</SlotPhysicalLocationCode>
                </AssociatedIOSlot>
            </ProfileIOSlot>
            <ProfileIOSlot schemaVersion="V1_0">
                <Metadata>
                    <Atom/>
                </Metadata>
                <AssociatedIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <BusGroupingRequired kb="CUD" kxe="false">false</BusGroupingRequired>
                    <Description kxe="false" kb="CUD">8 Gigabit PCI Express Dual Port Fibre Channel Adapter</Description>
                    <FeatureCodes kb="ROO" kxe="false">577D</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL58</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5273</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL2N</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5735</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL58</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5273</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">EL2N</FeatureCodes>
                    <FeatureCodes kb="ROO" kxe="false">5735</FeatureCodes>
                    <IOUnitPhysicalLocation kb="ROR" kxe="false">U78D3.001.WZS069F</IOUnitPhysicalLocation>
                    <PCAdapterID kxe="false" kb="ROO">61696</PCAdapterID>
                    <PCIClass kxe="false" kb="ROO">3076</PCIClass>
                    <PCIDeviceID kb="ROO" kxe="false">61696</PCIDeviceID>
                    <PCISubsystemDeviceID kb="ROO" kxe="false">906</PCISubsystemDeviceID>
                    <PCIManufacturerID kxe="false" kb="ROO">4319</PCIManufacturerID>
                    <PCIRevisionID kb="ROO" kxe="false">3</PCIRevisionID>
                    <PCIVendorID kb="ROO" kxe="false">4319</PCIVendorID>
                    <PCISubsystemVendorID kxe="false" kb="ROO">4116</PCISubsystemVendorID>
                    <RelatedIBMiIOSlot kxe="false" kb="CUD" schemaVersion="V1_0">
                        <Metadata>
                            <Atom/>
                        </Metadata>
                        <AlternateLoadSourceAttached kb="ROR" kxe="false">false</AlternateLoadSourceAttached>
                        <ConsoleCapable kxe="false" kb="ROR">false</ConsoleCapable>
                        <DirectOperationsConsoleCapable kb="ROR" kxe="false">false</DirectOperationsConsoleCapable>
                        <IOP kb="ROR" kxe="false">false</IOP>
                        <IOPInfoStale kb="ROR" kxe="false">false</IOPInfoStale>
                        <IOPoolID kb="ROR" kxe="false">65535</IOPoolID>
                        <LANConsoleCapable kxe="false" kb="ROR">false</LANConsoleCapable>
                        <LoadSourceAttached kxe="false" kb="ROR">false</LoadSourceAttached>
                        <LoadSourceCapable kxe="false" kb="ROR">false</LoadSourceCapable>
                        <OperationsConsoleAttached kb="ROR" kxe="false">false</OperationsConsoleAttached>
                        <OperationsConsoleCapable kxe="false" kb="ROR">false</OperationsConsoleCapable>
                    </RelatedIBMiIOSlot>
                    <RelatedIOAdapter kxe="false" kb="CUD">
                        <PhysicalFibreChannelAdapter schemaVersion="V1_0">
                            <Metadata>
                                <Atom/>
                            </Metadata>
                            <AdapterID kxe="false" kb="ROR">553713698</AdapterID>
                            <Description kb="CUD" kxe="false">8 Gigabit PCI Express Dual Port Fibre Channel Adapter</Description>
                            <DeviceName kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C3</DeviceName>
                            <DynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C3</DynamicReconfigurationConnectorName>
                            <PhysicalLocation kxe="false" kb="ROR">C3</PhysicalLocation>
                            <PhysicalFibreChannelPorts kb="CUD" kxe="false" schemaVersion="V1_0">
                                <Metadata>
                                    <Atom/>
                                </Metadata>
                                <PhysicalFibreChannelPort schemaVersion="V1_0">
                                    <Metadata>
                                        <Atom/>
                                    </Metadata>
                                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C3-T2</LocationCode>
                                    <PhysicalVolumes group="ViosStorage" kb="CUD" kxe="true" schemaVersion="V1_0">
                                        <Metadata>
                                            <Atom/>
                                        </Metadata>
                                    </PhysicalVolumes>
                                    <PortName kxe="false" kb="CUR">fcs3</PortName>
                                    <UniqueDeviceID kxe="false" kb="ROR">1aU78D3.001.WZS069F-P1-C3-T2</UniqueDeviceID>
                                    <WWPN kxe="false" kb="CUR">10000000c9be7095</WWPN>
                                    <WWNN ksv="V1_3_0" kb="ROO" kxe="false">20000000c9be7095</WWNN>
                                    <AvailablePorts kb="ROR" kxe="true">64</AvailablePorts>
                                    <TotalPorts kxe="true" kb="ROR">64</TotalPorts>
                                </PhysicalFibreChannelPort>
                                <PhysicalFibreChannelPort schemaVersion="V1_0">
                                    <Metadata>
                                        <Atom/>
                                    </Metadata>
                                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C3-T1</LocationCode>
                                    <PhysicalVolumes group="ViosStorage" kb="CUD" kxe="true" schemaVersion="V1_0">
                                        <Metadata>
                                            <Atom/>
                                        </Metadata>
                                    </PhysicalVolumes>
                                    <PortName kxe="false" kb="CUR">fcs2</PortName>
                                    <UniqueDeviceID kxe="false" kb="ROR">1aU78D3.001.WZS069F-P1-C3-T1</UniqueDeviceID>
                                    <WWPN kxe="false" kb="CUR">10000000c9be7094</WWPN>
                                    <WWNN ksv="V1_3_0" kb="ROO" kxe="false">20000000c9be7094</WWNN>
                                    <AvailablePorts kb="ROR" kxe="true">64</AvailablePorts>
                                    <TotalPorts kxe="true" kb="ROR">64</TotalPorts>
                                </PhysicalFibreChannelPort>
                            </PhysicalFibreChannelPorts>
                        </PhysicalFibreChannelAdapter>
                    </RelatedIOAdapter>
                    <SlotDynamicReconfigurationConnectorIndex kxe="false" kb="ROR">553713698</SlotDynamicReconfigurationConnectorIndex>
                    <SlotDynamicReconfigurationConnectorName kb="CUD" kxe="false">U78D3.001.WZS069F-P1-C3</SlotDynamicReconfigurationConnectorName>
                    <SlotPhysicalLocationCode kxe="false" kb="ROR">C3</SlotPhysicalLocationCode>
                </AssociatedIOSlot>
            </ProfileIOSlot>
        </ProfileIOSlots>
        <CurrentMaximumVirtualIOSlots kb="ROR" kxe="false">400</CurrentMaximumVirtualIOSlots>
    </PartitionIOConfiguration>
    <PartitionMemoryConfiguration kxe="false" kb="CUD" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <ActiveMemoryExpansionEnabled kb="CUD" kxe="false">false</ActiveMemoryExpansionEnabled>
        <ActiveMemorySharingEnabled kb="CUD" kxe="false">false</ActiveMemorySharingEnabled>
        <DesiredMemory kb="CUD" kxe="false">32768</DesiredMemory>
        <ExpansionFactor kb="CUD" kxe="false">0.0</ExpansionFactor>
        <HardwarePageTableRatio kb="CUD" kxe="false">7</HardwarePageTableRatio>
        <MaximumMemory kb="CUD" kxe="false">32768</MaximumMemory>
        <MinimumMemory kxe="false" kb="CUD">32768</MinimumMemory>
        <CurrentExpansionFactor kxe="false" kb="ROR">0.0</CurrentExpansionFactor>
        <CurrentHardwarePageTableRatio kb="ROR" kxe="false">7</CurrentHardwarePageTableRatio>
        <CurrentHugePageCount kxe="false" kb="ROR">0</CurrentHugePageCount>
        <CurrentMaximumHugePageCount kb="ROR" kxe="false">0</CurrentMaximumHugePageCount>
        <CurrentMaximumMemory kxe="false" kb="ROR">32768</CurrentMaximumMemory>
        <CurrentMemory kb="ROR" kxe="false">32768</CurrentMemory>
        <CurrentMinimumHugePageCount kb="ROR" kxe="false">0</CurrentMinimumHugePageCount>
        <CurrentMinimumMemory kb="ROR" kxe="false">32768</CurrentMinimumMemory>
        <MemoryExpansionHardwareAccessEnabled kxe="false" kb="ROR">true</MemoryExpansionHardwareAccessEnabled>
        <MemoryEncryptionHardwareAccessEnabled kxe="false" kb="ROR">true</MemoryEncryptionHardwareAccessEnabled>
        <MemoryExpansionEnabled kb="ROR" kxe="false">false</MemoryExpansionEnabled>
        <RedundantErrorPathReportingEnabled kb="ROR" kxe="false">false</RedundantErrorPathReportingEnabled>
        <RuntimeHugePageCount kb="ROR" kxe="false">0</RuntimeHugePageCount>
        <RuntimeMemory kxe="false" kb="ROR">32768</RuntimeMemory>
        <RuntimeMinimumMemory kxe="false" kb="ROR">32768</RuntimeMinimumMemory>
        <SharedMemoryEnabled kb="CUD" kxe="false">false</SharedMemoryEnabled>
        <PhysicalPageTableRatio ksv="V1_6_0" kxe="false" kb="CUD">6</PhysicalPageTableRatio>
    </PartitionMemoryConfiguration>
    <PartitionName kxe="false" kb="CUR">VIOS17-C340F2U03-ZZ</PartitionName>
    <PartitionProcessorConfiguration kxe="false" kb="CUD" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <DedicatedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DesiredProcessors kxe="false" kb="CUD">1</DesiredProcessors>
            <MaximumProcessors kb="CUD" kxe="false">1</MaximumProcessors>
            <MinimumProcessors kb="CUD" kxe="false">1</MinimumProcessors>
        </DedicatedProcessorConfiguration>
        <HasDedicatedProcessors kb="CUD" kxe="false">true</HasDedicatedProcessors>
        <SharedProcessorConfiguration kb="CUD" kxe="false" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
        </SharedProcessorConfiguration>
        <SharingMode kb="CUD" kxe="false">keep idle procs</SharingMode>
        <CurrentHasDedicatedProcessors kxe="false" kb="ROR">true</CurrentHasDedicatedProcessors>
        <CurrentSharingMode kb="ROR" kxe="false">keep idle procs</CurrentSharingMode>
        <CurrentDedicatedProcessorConfiguration kxe="false" kb="ROR" schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <CurrentMaximumProcessors kxe="false" kb="ROR">1</CurrentMaximumProcessors>
            <CurrentMinimumProcessors kxe="false" kb="ROR">1</CurrentMinimumProcessors>
            <CurrentProcessors kb="ROR" kxe="false">1</CurrentProcessors>
            <RunProcessors kxe="false" kb="ROR">1</RunProcessors>
        </CurrentDedicatedProcessorConfiguration>
        <RuntimeHasDedicatedProcessors kxe="false" kb="ROR">true</RuntimeHasDedicatedProcessors>
    </PartitionProcessorConfiguration>
    <PartitionProfiles kxe="false" kb="CUD">
        <link href="https://9.47.88.249:443/rest/api/uom/VirtualIOServer/5F2BF488-D5E5-43AC-BAB2-7D20C22C26C8/LogicalPartitionProfile/1ee06cd2-2fc8-3dee-ae85-acae7542cb7e" rel="related"/>
    </PartitionProfiles>
    <PartitionState kb="ROO" kxe="false">running</PartitionState>
    <PartitionType kb="COD" kxe="false">Virtual IO Server</PartitionType>
    <PartitionUUID kxe="false" kb="ROO">5F2BF488-D5E5-43AC-BAB2-7D20C22C26C8</PartitionUUID>
    <PendingProcessorCompatibilityMode kxe="false" kb="CUD">default</PendingProcessorCompatibilityMode>
    <ProgressPartitionDataRemaining kxe="false" kb="ROR">0</ProgressPartitionDataRemaining>
    <ProgressPartitionDataTotal kxe="false" kb="ROR">0</ProgressPartitionDataTotal>
    <ResourceMonitoringControlState kxe="false" kb="ROR">active</ResourceMonitoringControlState>
    <ResourceMonitoringIPAddress kb="CUD" kxe="false">9.47.92.83</ResourceMonitoringIPAddress>
    <AssociatedManagedSystem kxe="false" kb="CUD" href="https://9.47.88.249:443/rest/api/uom/ManagedSystem/d82ac4d6-054a-312c-8719-45d6c4a789a7" rel="related"/>
    <ClientNetworkAdapters kb="CUR" kxe="false"/>
    <MACAddressPrefix kxe="false" kb="ROR">236076614431232</MACAddressPrefix>
    <PhysicalVolumes group="ViosStorage" kxe="false" kb="CUD" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <PhysicalVolume schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <Description kxe="false" kb="CUD">SAS RAID 0 Disk Array</Description>
            <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C49-L20771AFE00-L0</LocationCode>
            <ReservePolicy kb="CUD" kxe="false">NoReserve</ReservePolicy>
            <ReservePolicyAlgorithm kb="CUD" kxe="false">Failover</ReservePolicyAlgorithm>
            <UniqueDeviceID kb="ROR" kxe="false">01MUlCTSAgICAgSVBSLTAgICA3NzFBRkUwMDAwMDAwMDIw</UniqueDeviceID>
            <AvailableForUsage kb="CUD" kxe="false">false</AvailableForUsage>
            <VolumeCapacity kxe="false" kb="CUR">544792</VolumeCapacity>
            <VolumeName kb="CUR" kxe="false">hdisk0</VolumeName>
            <VolumeState kb="ROR" kxe="false">active</VolumeState>
            <VolumeUniqueID kxe="false" kb="ROR">391BIBMIPR-0   771AFE000000002010IPR-0   771AFE0003IBMsas</VolumeUniqueID>
            <IsFibreChannelBacked kb="ROR" kxe="false">false</IsFibreChannelBacked>
            <IsISCSIBacked ksv="V1_8_0" kb="ROR" kxe="false">false</IsISCSIBacked>
            <StorageLabel ksv="V1_3_0" kxe="false" kb="ROR">VU5LTk9XTg==</StorageLabel>
            <DescriptorPage83 ksv="V1_5_0" kb="ROR" kxe="false">SUJNICAgICBJUFItMCAgIDc3MUFGRTAwMDAwMDAwMjA=</DescriptorPage83>
        </PhysicalVolume>
        <PhysicalVolume schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <Description kxe="false" kb="CUD">SAS RAID 0 Disk Array</Description>
            <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C49-L40771AFE00-L0</LocationCode>
            <ReservePolicy kb="CUD" kxe="false">NoReserve</ReservePolicy>
            <ReservePolicyAlgorithm kb="CUD" kxe="false">Failover</ReservePolicyAlgorithm>
            <UniqueDeviceID kb="ROR" kxe="false">01MUlCTSAgICAgSVBSLTAgICA3NzFBRkUwMDAwMDAwMDQw</UniqueDeviceID>
            <AvailableForUsage kb="CUD" kxe="false">true</AvailableForUsage>
            <VolumeCapacity kxe="false" kb="CUR">544792</VolumeCapacity>
            <VolumeName kb="CUR" kxe="false">hdisk1</VolumeName>
            <VolumeState kb="ROR" kxe="false">active</VolumeState>
            <VolumeUniqueID kxe="false" kb="ROR">391BIBMIPR-0   771AFE000000004010IPR-0   771AFE0003IBMsas</VolumeUniqueID>
            <IsFibreChannelBacked kb="ROR" kxe="false">false</IsFibreChannelBacked>
            <IsISCSIBacked ksv="V1_8_0" kb="ROR" kxe="false">false</IsISCSIBacked>
            <StorageLabel ksv="V1_3_0" kxe="false" kb="ROR">VU5LTk9XTg==</StorageLabel>
            <DescriptorPage83 ksv="V1_5_0" kb="ROR" kxe="false">SUJNICAgICBJUFItMCAgIDc3MUFGRTAwMDAwMDAwNDA=</DescriptorPage83>
        </PhysicalVolume>
    </PhysicalVolumes>
    <StoragePools group="ViosStorage" kxe="false" kb="CUD">
        <link href="https://9.47.88.249:443/rest/api/uom/VirtualIOServer/5F2BF488-D5E5-43AC-BAB2-7D20C22C26C8/VolumeGroup/b14527fc-e2c9-3f25-9ac4-52fd919b3ed6" rel="related"/>
    </StoragePools>
    <TrunkAdapters group="ViosNetwork" kb="CUD" kxe="false" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <TrunkAdapter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DynamicReconfigurationConnectorName kxe="false" kb="CUD">U9009.22G.138C5AA-V1-C2</DynamicReconfigurationConnectorName>
            <LocationCode kxe="false" kb="ROR">U9009.22G.138C5AA-V1-C2</LocationCode>
            <LocalPartitionID kb="CUR" kxe="false">1</LocalPartitionID>
            <RequiredAdapter kb="CUD" kxe="false">false</RequiredAdapter>
            <VariedOn kb="CUD" kxe="true">true</VariedOn>
            <VirtualSlotNumber kb="COD" kxe="false">2</VirtualSlotNumber>
            <AllowedOperatingSystemMACAddresses kxe="false" kb="CUD">ALL</AllowedOperatingSystemMACAddresses>
            <MACAddress kb="CUR" kxe="false">D6B5DEBE3202</MACAddress>
            <PortVLANID kxe="false" kb="CUR">2231</PortVLANID>
            <QualityOfServicePriorityEnabled kb="CUD" kxe="false">false</QualityOfServicePriorityEnabled>
            <TaggedVLANSupported kxe="false" kb="CUA">true</TaggedVLANSupported>
            <AssociatedVirtualSwitch kxe="false" kb="CUD">
                <link href="https://9.47.88.249:443/rest/api/uom/ManagedSystem/d82ac4d6-054a-312c-8719-45d6c4a789a7/VirtualSwitch/c82e10a0-a4cd-33f9-a935-eea379fecc44" rel="related"/>
            </AssociatedVirtualSwitch>
            <VirtualSwitchID kxe="false" kb="ROR">0</VirtualSwitchID>
            <VirtualSwitchName ksv="V1_12_0" kxe="false" kb="ROR">ETHERNET0</VirtualSwitchName>
            <DeviceName kb="ROR" kxe="false">ent8</DeviceName>
            <HCNID ksv="V1_10_0" kxe="false" kb="ROR">0</HCNID>
            <TrunkPriority kxe="false" kb="CUD">1</TrunkPriority>
        </TrunkAdapter>
        <TrunkAdapter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <DynamicReconfigurationConnectorName kxe="false" kb="CUD">U9009.22G.138C5AA-V1-C3</DynamicReconfigurationConnectorName>
            <LocationCode kxe="false" kb="ROR">U9009.22G.138C5AA-V1-C3</LocationCode>
            <LocalPartitionID kb="CUR" kxe="false">1</LocalPartitionID>
            <RequiredAdapter kb="CUD" kxe="false">false</RequiredAdapter>
            <VariedOn kb="CUD" kxe="true">true</VariedOn>
            <VirtualSlotNumber kb="COD" kxe="false">3</VirtualSlotNumber>
            <AllowedOperatingSystemMACAddresses kxe="false" kb="CUD">ALL</AllowedOperatingSystemMACAddresses>
            <MACAddress kb="CUR" kxe="false">D6B5DEBE3203</MACAddress>
            <PortVLANID kxe="false" kb="CUR">4094</PortVLANID>
            <QualityOfServicePriorityEnabled kb="CUD" kxe="false">false</QualityOfServicePriorityEnabled>
            <TaggedVLANIDs kb="CUA" kxe="false">2133 2173</TaggedVLANIDs>
            <TaggedVLANSupported kxe="false" kb="CUA">true</TaggedVLANSupported>
            <AssociatedVirtualSwitch kxe="false" kb="CUD">
                <link href="https://9.47.88.249:443/rest/api/uom/ManagedSystem/d82ac4d6-054a-312c-8719-45d6c4a789a7/VirtualSwitch/c82e10a0-a4cd-33f9-a935-eea379fecc44" rel="related"/>
            </AssociatedVirtualSwitch>
            <VirtualSwitchID kxe="false" kb="ROR">0</VirtualSwitchID>
            <VirtualSwitchName ksv="V1_12_0" kxe="false" kb="ROR">ETHERNET0</VirtualSwitchName>
            <DeviceName kb="ROR" kxe="false">ent10</DeviceName>
            <HCNID ksv="V1_10_0" kxe="false" kb="ROR">0</HCNID>
            <TrunkPriority kxe="false" kb="CUD">1</TrunkPriority>
        </TrunkAdapter>
    </TrunkAdapters>
    <VirtualIOServerLicenseAccepted kb="CUD" kxe="false">true</VirtualIOServerLicenseAccepted>
    <VirtualFibreChannelMappings group="ViosFCMapping" kb="CUD" kxe="false" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
    </VirtualFibreChannelMappings>
    <VirtualSCSIMappings group="ViosSCSIMapping" kxe="false" kb="CUD" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
        <VirtualSCSIMapping schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
            <TargetDevice kb="CUR" kxe="false">
                <VirtualOpticalTargetDevice schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <LogicalUnitAddress kb="CUR" kxe="false">0x8200000000000000</LogicalUnitAddress>
                    <TargetName kb="CUR" kxe="false">vtopt0</TargetName>
                    <UniqueDeviceID kxe="false" kb="ROR">19f2a61b0c3176273b</UniqueDeviceID>
                </VirtualOpticalTargetDevice>
            </TargetDevice>
        </VirtualSCSIMapping>
        <VirtualSCSIMapping schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <AssociatedLogicalPartition kb="CUR" kxe="false" href="https://{hmc_host}/rest/api/uom/ManagedSystem/{system_uuid}/LogicalPartition/{partition_uuid}" rel="related"/>
            <Storage kxe="false" kb="CUR">
                <PhysicalVolume schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <Description kxe="false" kb="CUD">SAS RAID 0 Disk Array</Description>
                    <LocationCode kxe="false" kb="ROR">U78D3.001.WZS069F-P1-C49-L40771AFE00-L0</LocationCode>
                    <ReservePolicy kb="CUD" kxe="false">NoReserve</ReservePolicy>
                    <ReservePolicyAlgorithm kb="CUD" kxe="false">Failover</ReservePolicyAlgorithm>
                    <AvailableForUsage kb="CUD" kxe="false">true</AvailableForUsage>
                    <VolumeCapacity kxe="false" kb="CUR">544792</VolumeCapacity>
                    <VolumeName kb="CUR" kxe="false">{physical_volume_name}</VolumeName>
                    <VolumeState kb="ROR" kxe="false">active</VolumeState>
                    <IsFibreChannelBacked kb="ROR" kxe="false">false</IsFibreChannelBacked>
                    <IsISCSIBacked ksv="V1_8_0" kb="ROR" kxe="false">false</IsISCSIBacked>
                    <StorageLabel ksv="V1_3_0" kxe="false" kb="ROR">VU5LTk9XTg==</StorageLabel>
                    <DescriptorPage83 ksv="V1_5_0" kb="ROR" kxe="false">SUJNICAgICBJUFItMCAgIDc3MUFGRTAwMDAwMDAwNDA=</DescriptorPage83>
                </PhysicalVolume>
            </Storage>
            <TargetDevice kb="CUR" kxe="false">
                <PhysicalVolumeVirtualTargetDevice schemaVersion="V1_0">
                    <Metadata>
                        <Atom/>
                    </Metadata>
                    <LogicalUnitAddress kb="CUR" kxe="false">0x8100000000000000</LogicalUnitAddress>
                    <TargetName kb="CUR" kxe="false">test</TargetName>
                    <UniqueDeviceID kxe="false" kb="ROR">081d000521accf4fc</UniqueDeviceID>
                </PhysicalVolumeVirtualTargetDevice>
            </TargetDevice>
        </VirtualSCSIMapping>
    </VirtualSCSIMappings>
    <FibreChannelPortLabelCapable group="ViosStorage" ksv="V1_12_0" kb="CUD" kxe="false">true</FibreChannelPortLabelCapable>
</VirtualIOServer:VirtualIOServer>
'''

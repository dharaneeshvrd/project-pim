CONTENT_TYPE = "application/vnd.ibm.powervm.web+xml; Type=JobRequest"
PAYLOAD = '''
<JobRequest
 xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/"  xmlns:ns2="http://www.w3.org/XML/1998/namespace/k2" schemaVersion="V1_0">
 <Metadata>
  <Atom/>
 </Metadata>
 <RequestedOperation kxe="false" kb="CUR" schemaVersion="V1_0">
  <Metadata>
   <Atom/>
  </Metadata>
  <OperationName kxe="false" kb="ROR">PowerOn</OperationName>
  <GroupName kxe="false" kb="ROR">LogicalPartition</GroupName>
 </RequestedOperation>
<JobParameters kb="CUR" kxe="false" schemaVersion="V1_0">
        <Metadata>
            <Atom/>
        </Metadata>
	  <JobParameter schemaVersion="V1_0">
           <Metadata>
               <Atom/>
           </Metadata>
           <ParameterName kxe="false" kb="ROR">force</ParameterName>
           <ParameterValue kxe="false" kb="CUR">false</ParameterValue>
      </JobParameter>
      <JobParameter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <ParameterName kxe="false" kb="ROR">LogicalPartitionProfile</ParameterName>
            <ParameterValue kxe="false" kb="CUR">lpar_prof</ParameterValue>
        </JobParameter>
		<JobParameter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <ParameterName kxe="false" kb="ROR">novsi</ParameterName>
            <ParameterValue kxe="false" kb="CUR">true</ParameterValue>
        </JobParameter>
		<JobParameter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <ParameterName kxe="false" kb="ROR">bootmode</ParameterName>
            <ParameterValue kxe="false" kb="CUR">norm</ParameterValue>
        </JobParameter>
		<JobParameter schemaVersion="V1_0">
            <Metadata>
                <Atom/>
            </Metadata>
            <ParameterName kxe="false" kb="ROR">keylock</ParameterName>
            <ParameterValue kxe="false" kb="CUR">manual</ParameterValue>
        </JobParameter>
   </JobParameters>
</JobRequest>
'''
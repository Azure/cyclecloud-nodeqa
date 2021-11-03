# Azure Cyclecloud Node QA

This project will qualify individual nodes before they join a cluster. 

For failing nodes you may see something like this in the message queue:

```Log
Cyclecloud-NodeQA (NodeName:hpc-pg0-1/Hostname:ip-0A010A06/VMId:af4d08e9-1273-4bfc-babc-84a6a9e19c71) 
Cyclecloud-NodeQA ERROR: Device 0 measured 21.8 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 1 measured 21.8 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 2 measured 21.7 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 3 measured 21.7 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 4 measured 21.8 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 5 measured 21.8 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 6 measured 21.8 GB/s BW, expected 23 
Cyclecloud-NodeQA ERROR: Device 7 measured 21.8 GB/s BW, expected 23
```

The VM metadata will be written to a file on the node `/tmp/NodeQA` but 
will only be available for short amount of time because this project will
delete failing nodes.

Manually started nodes will be removed. Nodes that are autoscaled will 
be replaced but manually added nodes will not.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

